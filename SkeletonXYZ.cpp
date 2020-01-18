// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include <k4a/k4a.h>
#include <k4abt.h>
#include <time.h>

#undef UNICODE

#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
#include <iostream>
#include <sstream> 
// Need to link with Ws2_32.lib
#pragma comment (lib, "Ws2_32.lib")
// #pragma comment (lib, "Mswsock.lib")
#define DEFAULT_BUFLEN 1024
#define DEFAULT_PORT "27014"

HANDLE ghEvents[1];

#define GLFW_KEY_ESCAPE   256


#define VERIFY(result, error)                                                                            \
    if(result != K4A_RESULT_SUCCEEDED)                                                                   \
    {                                                                                                    \
        printf("%s \n - (File: %s, Function: %s, Line: %d)\n", error, __FILE__, __FUNCTION__, __LINE__); \
        exit(1);                                                                                         \
    }                                                                                                    \

// Global State and Key Process Function
bool s_isRunning = true;
int64_t ProcessKey(void* /*context*/, int key)
{
	// https://www.glfw.org/docs/latest/group__keys.html
	switch (key)
	{
		// Quit
	case GLFW_KEY_ESCAPE:
		s_isRunning = false;
		break;
	}
	return 1;
}

int64_t CloseCallback(void* /*context*/)
{
	s_isRunning = false;
	return 1;
}

typedef struct ThreadData
{
	char* recvbuf;
} THREADDATA, * PTHREADDATA;

DWORD WINAPI myThread(LPVOID lpParameter)
{
	PTHREADDATA pDataStruct = ((PTHREADDATA)lpParameter);
	WSADATA wsaData;
	int iResult;
	DWORD dwEvent;
	SOCKET ListenSocket = INVALID_SOCKET;

	struct addrinfo* result = NULL;
	struct addrinfo hints;

	int iSendResult;
	char* recvbuf = pDataStruct->recvbuf;
	int recvbuflen = DEFAULT_BUFLEN;

	// Initialize Winsock
	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
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
	iResult = getaddrinfo(NULL, DEFAULT_PORT, &hints, &result);
	if (iResult != 0) {
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
			1,           // number of objects in array
			ghEvents,     // array of objects
			FALSE,       // wait for any object
			INFINITE);
		int i = sendto(ListenSocket, recvbuf, 1024, 0, result->ai_addr, result->ai_addrlen);
		if (i == -1)
			std::cout << "Error sending the packet\n";
	//	Sleep(1000);
	}
	WSACleanup();
	return 0;
}



int main()
{

	unsigned int myCounter = 0;
	DWORD myThreadID;
	PTHREADDATA pDataStruct;
	pDataStruct = (PTHREADDATA)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(THREADDATA));
	pDataStruct->recvbuf = (char*)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, DEFAULT_BUFLEN);
	HANDLE myHandle = CreateThread(0, 0, myThread, pDataStruct, 0, &myThreadID);

	std::stringstream buffer;
	ZeroMemory(pDataStruct->recvbuf, sizeof(pDataStruct->recvbuf));

	for (DWORD i = 0; i < 1; i++)
	{
		ghEvents[i] = CreateEvent(
			NULL,   // default security attributes
			FALSE,  // auto-reset event object
			FALSE,  // initial state is nonsignaled
			NULL);  // unnamed object

		if (ghEvents[i] == NULL)
		{
			printf("CreateEvent error: %d\n", GetLastError());
			ExitProcess(0);
		}
	}
	
	


	k4a_device_configuration_t device_config = K4A_DEVICE_CONFIG_INIT_DISABLE_ALL;
	device_config.depth_mode = K4A_DEPTH_MODE_NFOV_UNBINNED;

	k4a_device_t device;
	VERIFY(k4a_device_open(0, &device), "Open K4A Device failed!");
	VERIFY(k4a_device_start_cameras(device, &device_config), "Start K4A cameras failed!");

	k4a_calibration_t sensor_calibration;
	VERIFY(k4a_device_get_calibration(device, device_config.depth_mode, K4A_COLOR_RESOLUTION_OFF, &sensor_calibration),
		"Get depth camera calibration failed!");

	k4abt_tracker_t tracker = NULL;
	k4abt_tracker_configuration_t tracker_config = K4ABT_TRACKER_CONFIG_DEFAULT;
	VERIFY(k4abt_tracker_create(&sensor_calibration, tracker_config, &tracker), "Body tracker initialization failed!");


	time_t t;
	int count = 0;

	int frame_count = 0;
	while (s_isRunning)//do
	{
		k4a_capture_t sensor_capture;
		k4a_wait_result_t get_capture_result = k4a_device_get_capture(device, &sensor_capture, K4A_WAIT_INFINITE);
		if (get_capture_result == K4A_WAIT_RESULT_SUCCEEDED)
		{
			frame_count++;
			//printf("Start processing frame %d\n", frame_count);
			k4a_wait_result_t queue_capture_result = k4abt_tracker_enqueue_capture(tracker, sensor_capture, K4A_WAIT_INFINITE);
			k4a_capture_release(sensor_capture);
			if (queue_capture_result == K4A_WAIT_RESULT_TIMEOUT)
			{
				// It should never hit timeout when K4A_WAIT_INFINITE is set.
				printf("Error! Add capture to tracker process queue timeout!\n");
				break;
			}
			else if (queue_capture_result == K4A_WAIT_RESULT_FAILED)
			{
	
				printf("Error! Add capture to tracker process queue failed!\n");
				break;
			}

			k4abt_frame_t body_frame = NULL;
			k4a_wait_result_t pop_frame_result = k4abt_tracker_pop_result(tracker, &body_frame, K4A_WAIT_INFINITE);
			if (pop_frame_result == K4A_WAIT_RESULT_SUCCEEDED)
			{
				size_t num_bodies = k4abt_frame_get_num_bodies(body_frame);
				printf("%zu bodies are detected!\n", num_bodies);

				time_t now;
				time(&now);

				//printf("%ld", now);
				buffer.str("");
				buffer << "[" << now << ", " << "[";
				for (size_t i = 0; i < num_bodies; i++)
				{
					k4abt_body_t body;
					VERIFY(k4abt_frame_get_body_skeleton(body_frame, i, &body.skeleton), "Get body from body frame failed!");
					body.id = k4abt_frame_get_body_id(body_frame, i);
					//print_body_information(body, fp);
					//printf("Body ID: %u,", body.id);
					//printf("%u, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n", body.id, body.skeleton.joints[2].position.v[0], body.skeleton.joints[2].position.v[1], body.skeleton.joints[2].position.v[2],
					//	body.skeleton.joints[5].position.v[0], body.skeleton.joints[5].position.v[1], body.skeleton.joints[5].position.v[2],
					//	body.skeleton.joints[12].position.v[0], body.skeleton.joints[12].position.v[1], body.skeleton.joints[12].position.v[2],
					//	body.skeleton.joints[19].position.v[0], body.skeleton.joints[19].position.v[1], body.skeleton.joints[19].position.v[2],
					//	body.skeleton.joints[23].position.v[0], body.skeleton.joints[23].position.v[1], body.skeleton.joints[23].position.v[2]
					//);//SPINE_CHEST, SHOULDER_LEFT, SHOULDER_RIGHT, KNEE_LEFT, KNEE_RIGHT
					buffer << "[" << body.id \
						   << ", " << body.skeleton.joints[2].position.v[0] \
						   << ", " << body.skeleton.joints[2].position.v[1] \
						   << ", " << body.skeleton.joints[2].position.v[2] \
						   << "]";
					if (num_bodies > 1 && i!= num_bodies-1)
					{
						buffer << " ,";
					}
				}
				buffer << "]]";
				k4abt_frame_release(body_frame);
			}
			else if (pop_frame_result == K4A_WAIT_RESULT_TIMEOUT)
			{
				//  It should never hit timeout when K4A_WAIT_INFINITE is set.
				printf("Error! Pop body frame result timeout!\n");
				break;
			}
			else
			{
				printf("Pop body frame result failed!\n");
				break;
			}
		}
		else if (get_capture_result == K4A_WAIT_RESULT_TIMEOUT)
		{
			// It should never hit time out when K4A_WAIT_INFINITE is set.
			printf("Error! Get depth frame time out!\n");
			break;
		}
		else
		{
			printf("Get depth capture returned error: %d\n", get_capture_result);
			break;
		}
		//buffer.str("");
		//buffer << "hello world ";
		//buffer << count << '\n';
		std::cout << buffer.str() << '\n';
		//ZeroMemory(pDataStruct->recvbuf, sizeof(pDataStruct->recvbuf));
		memset(pDataStruct->recvbuf, 0, 1024);
		memcpy(pDataStruct->recvbuf, buffer.str().c_str(), buffer.str().length());
		count++;
		PulseEvent(ghEvents[0]);
		Sleep(1000);
	} //while ends

	printf("Finished body tracking processing!\n");
	k4abt_tracker_shutdown(tracker);
	k4abt_tracker_destroy(tracker);
	k4a_device_stop_cameras(device);
	k4a_device_close(device);
	CloseHandle(myHandle);
	return 0;
}