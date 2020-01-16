#undef UNICODE

#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdlib.h>
#include <stdio.h>
#include <string>
#include <iostream>
#include <sstream> 
// Need to link with Ws2_32.lib
#pragma comment (lib, "Ws2_32.lib")
// #pragma comment (lib, "Mswsock.lib")

#define DEFAULT_BUFLEN 1024
#define DEFAULT_PORT "27014"

typedef struct ThreadData 
{
    char* recvbuf;
} THREADDATA, *PTHREADDATA;


HANDLE ghEvents[1];

DWORD WINAPI myThread(LPVOID lpParameter)
{
	PTHREADDATA pDataStruct = ((PTHREADDATA)lpParameter);
    WSADATA wsaData;
    int iResult;
    DWORD dwEvent;
    SOCKET ListenSocket = INVALID_SOCKET;

    struct addrinfo *result = NULL;
    struct addrinfo hints;

    int iSendResult;
    char* recvbuf = pDataStruct->recvbuf;
    int recvbuflen = DEFAULT_BUFLEN;
    
    // Initialize Winsock
    iResult = WSAStartup(MAKEWORD(2,2), &wsaData);
    if (iResult != 0) {
        printf("WSAStartup failed with error: %d\n", iResult);
        return 1;
    }

    ZeroMemory(&hints, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_protocol = IPPROTO_UDP;
    // hints.ai_flags = AI_PASSIVE;

    // Resolve the server address and port
    iResult = getaddrinfo("127.0.0.1", DEFAULT_PORT, &hints, &result);
    // iResult = getaddrinfo("10.192.37.133", DEFAULT_PORT, &hints, &result);
    if ( iResult != 0 ) {
        printf("getaddrinfo failed with error: %d\n", iResult);
        WSACleanup();
        return 1;
    }

    // Create a SOCKET for connecting to server
    ListenSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if (ListenSocket == INVALID_SOCKET) {
        printf("socket failed with error: %ld\n", WSAGetLastError());
        freeaddrinfo(result);
        WSACleanup();
        return 1;
    }
    // int count = 0;
    // std::stringstream buffer;
    // ZeroMemory(recvbuf, sizeof(recvbuf));
    while (true)
    {

        dwEvent = WaitForMultipleObjects( 
            2,           // number of objects in array
            ghEvents,     // array of objects
            FALSE,       // wait for any object
            INFINITE);       // five-second wait
        int i = sendto(ListenSocket, recvbuf, 1024, 0, result->ai_addr, result->ai_addrlen);
        if (i == -1)
            std::cout << "Error sending the packet\n";
        // Sleep(1000);
    }
    WSACleanup();
	return 0;
}

int __cdecl main(void) 
{
    using namespace std;
	unsigned int myCounter = 0;
	DWORD myThreadID;
    PTHREADDATA pDataStruct;
    pDataStruct = (PTHREADDATA) HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(THREADDATA));
    pDataStruct->recvbuf = (char*) HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, DEFAULT_BUFLEN);
	HANDLE myHandle = CreateThread(0, 0, myThread, pDataStruct, 0, &myThreadID);    
    
    int count = 0;
    std::stringstream buffer;
    ZeroMemory(pDataStruct->recvbuf, sizeof(pDataStruct->recvbuf));

    DWORD dwEvent;
    for (DWORD i = 0; i < 1; i++) 
    { 
        ghEvents[i] = CreateEvent( 
            NULL,   // default security attributes
            FALSE,  // auto-reset event object
            FALSE,  // initial state is nonsignaled
            NULL);  // unnamed object

        if (ghEvents[i] == NULL) 
        { 
            printf("CreateEvent error: %d\n", GetLastError() ); 
            ExitProcess(0); 
        } 
    } 

    while (true)
    {
        // EnterCriticalSection (&BufferLock);
        buffer.str("");
        // memcpy(pDataStruct->recvbuf, buffer.str().c_str(), buffer.str().length()); 
        buffer << "hello world " << count << '\n';
        std::cout << buffer.str();
        memcpy(pDataStruct->recvbuf, buffer.str().c_str(), buffer.str().length()); 
        PulseEvent(ghEvents[0]);
        Sleep(1000);
        count++;
    }
    CloseHandle(myHandle);
    std::cout << myCounter << endl;
    return 0;
}
