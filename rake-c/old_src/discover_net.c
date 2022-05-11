#include <stdint.h>
#include <netdb.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(int argc, char *argv[])
{
    struct  netent *ne;
    struct hostent *he;

    uint32_t  hostorder, netorder;

    setnetent(1);           // open the network name database

    while(ne = getnetent()) {   // foreach network entry
	printf("NETWORK %s :\n", ne->n_name);
	hostorder = (ne->n_net << 8);

	sethostent(1);      // open the host name database

	for(int i=1 ; i<=254 ; i++) {
	    netorder = htonl(hostorder);
	    if(he = gethostbyaddr((char *)&netorder, sizeof(netorder), AF_INET)){
                printf("%36s : \n", he->h_name);
                ++hostorder;
            }
        }
        endhostent();       // close the host name database
    }
    endnetent();            // close the network name database
    
    return 0;
}