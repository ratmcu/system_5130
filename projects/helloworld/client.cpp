#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>

using namespace std;

#define PORT_NUM "27014"
#pragma comment (lib, "Ws2_32.lib")
#pragma comment (lib, "Mswsock.lib")
#pragma comment (lib, "AdvApi32.lib")
#define DEFAULT_BUFLEN 1024

int main()
{
    int ConnectSocket;
    addrinfo* sockInfo;
    addrinfo hints;

    //Initialize winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 0), &wsaData))
        cout << "Error initalizing winsock\n";

    //Get the address info of this program
    ZeroMemory(&hints, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = AI_PASSIVE;

    int check = getaddrinfo(NULL, PORT_NUM, &hints, &sockInfo);
    if (check != 0)
        cout << WSAGetLastError();

    //Get the socket
    cout << sockInfo->ai_family << " ," << sockInfo->ai_socktype << " ," << sockInfo->ai_protocol << '\n';
    ConnectSocket = socket(sockInfo->ai_family, sockInfo->ai_socktype, sockInfo->ai_protocol);
    if (ConnectSocket == -1)
        cout << "Error creating the socket\n";

    //Bind to the socket
        cout << ConnectSocket << " ," << sockInfo->ai_addr << " ," << sockInfo->ai_addrlen << '\n';
    if (bind(ConnectSocket, sockInfo->ai_addr, sockInfo->ai_addrlen) == -1)
        cout << "Error creating the socket\n";

    //Recieve data from the socket
    // Receive until the peer closes the connection
    char recvbuf[DEFAULT_BUFLEN];
    int iResult, iSendResult;
    int recvbuflen = DEFAULT_BUFLEN;
    do {
        // iSendResult = send(ConnectSocket, recvbuf, DEFAULT_BUFLEN, 0 );
        // if (iSendResult == SOCKET_ERROR) {
        //     printf("send failed with error: %d\n", WSAGetLastError());
        //     closesocket(ConnectSocket);
        //     WSACleanup();
        //     return 1;
        // }
        iResult = recv(ConnectSocket, recvbuf, recvbuflen, 0);
        if ( iResult > 0 ){
            printf("Bytes received: %d\n", iResult);
            cout << recvbuf << endl;
        }
        else if ( iResult == 0 )
            printf("Connection closed\n");
        else
            printf("recv failed with error: %d\n", WSAGetLastError());

    } while( 1);

    // cleanup
    closesocket(ConnectSocket);
    WSACleanup();

    return 1;
}