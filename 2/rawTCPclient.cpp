# include <unistd.h>
# include <sys/socket.h>
# include <sys/types.h>
#include  <arpa/inet.h>
# include <string.h>
# include <stdio.h>
# include <stdlib.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <netdb.h>
#include <stdio.h>    //for printf
#include <string.h> //memset
#include <sys/socket.h>    //for socket ofcourse
#include <stdlib.h> //for exit(0);
#include <errno.h> //For errno - the error number
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>

#include <sys/ioctl.h>
#include <net/if.h>
#include <iostream>
 

/*
    96 bit (12 bytes) pseudo header needed for tcp header checksum calculation
*/
struct pseudo_header
{
    u_int32_t source_address;
    u_int32_t dest_address;
    u_int8_t placeholder;
    u_int8_t protocol;
    u_int16_t tcp_length;
};

/*
    Generic checksum calculation function
*/
unsigned short csum(unsigned short *ptr,int nbytes)
{
    register long sum;
    unsigned short oddbyte;
    register short answer;

    sum=0;
    while(nbytes>1) {
        sum+=*ptr++;
        nbytes-=2;
    }
    if(nbytes==1) {
        oddbyte=0;
        *((u_char*)&oddbyte)=*(u_char*)ptr;
        sum+=oddbyte;
    }

    sum = (sum>>16)+(sum & 0xffff);
    sum = sum + (sum>>16);
    answer=(short)~sum;
    
    return(answer);
}

int main (void)
{
  
  int MAX_HOP = 30;
  
  //Create a raw socket
  int s = socket (PF_INET, SOCK_RAW, IPPROTO_TCP);
  
  if(s == -1)
  {
      //socket creation failed, may be because of non-root privileges
      perror("Failed to create socket");
      exit(1);
  }
  
  //Datagram to represent the packet
  char datagram[4096] , source_ip[32] , *data , *pseudogram, recvBuff[4096];
  
  //zero out the packet buffer
  memset (datagram, 0, 4096);
  
  //IP header
  struct ip *iph = (struct ip *) datagram;
  
  //TCP header
  struct tcphdr *tcph = (struct tcphdr *) (datagram + sizeof (struct ip));
  struct sockaddr_in sin;
  struct pseudo_header psh;
  
  //Data part
  data = datagram + sizeof(struct ip) + sizeof(struct tcphdr);
  strcpy(data , "ABCDEFGHIJKLMNOPQRSTUVWXYZ");

  //get system's IP address
  struct ifreq ifr;
  size_t if_name_len=strlen("enp0s3");
  if (if_name_len<sizeof(ifr.ifr_name)) {
    memcpy(ifr.ifr_name,"enp0s3",if_name_len);
    ifr.ifr_name[if_name_len]=0;
  } else {
    perror("interface name is too long");
  }
  
  int fd=socket(AF_INET,SOCK_DGRAM,0);
  if (fd==-1) {
    perror("Socket error:");
  }
  
  if (ioctl(fd,SIOCGIFADDR,&ifr)==-1) {
    int temp_errno=errno;
    close(fd);
    perror("IOCTL error");
  }
  close(fd);
  struct sockaddr_in* ipaddr = (struct sockaddr_in*)&ifr.ifr_addr;
  printf("IP address: %s\n",inet_ntoa(ipaddr->sin_addr));
  
  strcpy(source_ip , inet_ntoa(ipaddr->sin_addr)); //your system's IP address
  sin.sin_family = AF_INET;
  sin.sin_port = htons(80);
  
  // user enter dest
  char hostname[256];
  std::cout << "Please enter destination host name: ";
  std::cin >> hostname;
  
  struct hostent* destination;
  struct in_addr dest_addr;
  destination = gethostbyname ( hostname );
  if (destination == NULL) {
    perror("Error, no such host");
  } else {
    if (*destination->h_addr_list) {
      bcopy(*destination->h_addr_list++, (char *) &dest_addr, sizeof(dest_addr));
      printf("Traceroute to %s [%s], %d hops max:\n", hostname, inet_ntoa(dest_addr), MAX_HOP);
    }
  }
  
  sin.sin_addr.s_addr = inet_addr (inet_ntoa(dest_addr)); //user's input destination ip


  //Fill in the IP Header
  
  iph->ip_hl = 5;
  iph->ip_v = 4;
  iph->ip_tos = 0;
  iph->ip_len = sizeof (struct ip) + sizeof (struct tcphdr) + strlen(data);
  iph->ip_id = htons (12345);    //Id of this packet
  iph->ip_off = 0;
  iph->ip_ttl = 1;
  iph->ip_p = IPPROTO_TCP;
  iph->ip_sum = 0;        //Set to 0 before calculating checksum
  iph->ip_src.s_addr = inet_addr ( source_ip );    //Spoof the source ip address
  iph->ip_dst.s_addr = sin.sin_addr.s_addr;
 
  //Ip checksum
  iph->ip_sum = csum ((unsigned short *) datagram, iph->ip_len);
  
  //TCP Header
  tcph->th_sport = htons (1234);
  tcph->th_dport = htons (65535);
  tcph->th_seq = htonl(0);
  tcph->th_ack = 0;  //first SYN packet will not have ACK
  tcph->th_off = 5;    //tcp header size
  // tcph->th_off = sizeof(struct tcphdr)/4; /* data position in the packet */
  tcph->th_flags = TH_SYN; /* initial connection request */
  //tcph->th_flags = TH_PUSH;
  tcph->th_win = htons (5840);    /* maximum allowed window size */
  tcph->th_sum = 0;    //leave checksum 0 now, filled later by pseudo header
  tcph->th_urp = 0;
  
  //Now the TCP checksum
  psh.source_address = inet_addr( source_ip );
  psh.dest_address = sin.sin_addr.s_addr;
  psh.placeholder = 0;
  psh.protocol = IPPROTO_TCP;
  psh.tcp_length = htons(sizeof(struct tcphdr) + strlen(data) );
  
  int psize = sizeof(struct pseudo_header) + sizeof(struct tcphdr) + strlen(data);
  pseudogram = (char*) malloc(psize);
  
  memcpy(pseudogram , (char*) &psh , sizeof (struct pseudo_header));
  memcpy(pseudogram + sizeof(struct pseudo_header) , tcph , sizeof(struct tcphdr) + strlen(data));
  
  tcph->th_sum = csum( (unsigned short*) pseudogram , psize);
  
  //IP_HDRINCL to tell the kernel that headers are included in the packet
  int one = 1;
  const int *val = &one;
  
  if (setsockopt (s, IPPROTO_IP, IP_HDRINCL, val, sizeof (one)) < 0)
  {
      perror("Error setting IP_HDRINCL");
      exit(0);
  }
  
  // TO RECEIVE PACKET
  socklen_t len;
  long received;
  int sockfd;
  struct sockaddr_in cliaddr;
  int i;
  char* current_addr;
  char* intended_addr;
  
  // loop until you reach the destination
  int loop = 1;
  
  while (loop < MAX_HOP)
  {
//    printf("\nHop number :%d, packet TTL: %u\n", loop, iph->ip_ttl);
    //send the packet
    if (sendto (s, datagram, iph->ip_len, 0, (struct sockaddr *) &sin, sizeof (sin)) < 0)
    {
      perror("sendto failed");
    }
    else
    {
//      printf("Packet for hop %d Sent. Length: %d \n", loop, iph->ip_len);
      
      //Create a RAW socket (connection less)
      sockfd = socket(PF_INET, SOCK_RAW, IPPROTO_ICMP);
      if (sockfd < 0){
        perror("ICMP Socket Error");
        exit(1);
      }
      
      // set timeout
      struct timeval timeout;
      timeout.tv_sec = 0;
      timeout.tv_usec = 500000;
      setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
      
      len = sizeof(struct sockaddr_in);
      received = recvfrom(sockfd, recvBuff, sizeof(recvBuff), 0, (struct sockaddr *) &cliaddr, &len);
      
      if (received < 0) {
        perror("Recv Timeout");
        return 0;
        
      } else {
  
        //extract IP header from the buffer
        struct ip *ip_hdr = (struct ip *) recvBuff;
  
        //print all the values in the packet in Hex
        // for (i = 0; i < received; i++) {
        //     printf("%02X%s", (uint8_t) recvBuff[i], (i + 1) % 16 ? " " : "\n");
        // }
        // printf("\n");
  
        //extract ICMP header part
        struct icmp *icmp_hdr = (struct icmp *) ((char *) ip_hdr + (4 * ip_hdr->ip_hl));
  
        // extract IP inside ICMP, print only for TCP
        int protocol = icmp_hdr->icmp_ip.ip_p;
  
        if (protocol == 6)
        {
          printf("%d  %s\n", loop, inet_ntoa(cliaddr.sin_addr));
          printf("ICMP msg type=%d, code=%d\n", icmp_hdr->icmp_type, icmp_hdr->icmp_code );
        }
        else
        {
          printf("ICMP not for TCP\n");
        }
        
        if (icmp_hdr->icmp_type == 3) {
          
          // sanity check
          if (cliaddr.sin_addr.s_addr == dest_addr.s_addr) {
            printf("Reached!\n");
          }
          
          break;
        }
        
      }
      
    }
    
    iph->ip_ttl++;
  
    iph->ip_sum = csum ((unsigned short *) datagram, iph->ip_len);
    loop++;
  }
  
  return 0;
}

//Complete
