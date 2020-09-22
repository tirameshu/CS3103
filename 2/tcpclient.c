// gcc tcpclient.c
// ./a.out

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>


int main()

{
  int sock, bytes_recieved;
  char* send_data;
  char recv_data[1024];
  struct hostent *host;
  struct sockaddr_in server_addr;
  
  host = gethostbyname("nwtools.atwebpages.com");
  
  if (!host) {
    printf("host returns null\n");
  }
  
  //create a Socket structure   - "Client Socket"
  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
    perror("Socket");
    exit(1);
  }

//  printf("after socket creation\n");
  
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(80); // 80 for http
  server_addr.sin_addr = *((struct in_addr *)host->h_addr);
  bzero(&(server_addr.sin_zero),8);

  //connect to server
  if (connect(sock, (struct sockaddr*)&server_addr,
              sizeof(struct sockaddr)) == -1) {
    perror("Connect");
    exit(1);
  }

//  printf("\n I am conneted to (%s , %d)",
//         inet_ntoa(server_addr.sin_addr),ntohs(server_addr.sin_port));  //ntoa - forms dotted decimal notation

  //send data to server
  send_data = "GET /yourip.php HTTP/1.1\r\nHost: nwtools.atwebpages.com\r\n\r\n";
  send(sock,send_data,strlen(send_data), 0);

  //get reply from server
  bytes_recieved=recv(sock,recv_data,1024,0);
  recv_data[bytes_recieved] = '\0';

  //process data.
//  printf("\n%s ", recv_data);
  char *ptr;
  const char ip_addr[14] = "IP:";
  
  ptr = strstr(recv_data, ip_addr);
  int index = (int) (ptr - recv_data + 3);
  
  char sub[20];
  int sub_index = 0;
  
  while (recv_data[index] != 32) {
    sub[sub_index] = recv_data[index];
    sub_index++;
    index++;
  }
  
  sub[sub_index] = '\0';
  
  printf("My public IP address is %s\n", sub);
  
  return 0;
}
