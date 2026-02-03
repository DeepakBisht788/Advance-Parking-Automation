#include <stdio.h>   // Standard I/O functions  
#include <stdlib.h>  // Memory allocation functions  
#include <string.h>  // String handling functions  
#include <time.h>    // Time functions for arrival/exit timestamps  

//   Min-Heap for slot allocation  
//  
int heap[100];             // Array for min-heap to manage slots  
int heapSize = 0;          // Current size of the heap  

void swap(int *a, int *b) {
    int t = *a; *a = *b; *b = t; // Utility: Swap two ints  
}

void insertHeap(int slot) {
    // Insert a new slot number into the min-heap  
    heapSize++; heap[heapSize] = slot;
    int i = heapSize;
    while (i > 1 && heap[i] < heap[i / 2]) {
        swap(&heap[i], &heap[i / 2]);
        i /= 2;
    }
}

int extractMin() {
    // Remove and return minimum slot number  
    if (heapSize == 0) return -1;
    int min = heap[1];
    heap[1] = heap[heapSize]; heapSize--;
    int i = 1;
    while (i * 2 <= heapSize) {
        int child = i * 2;
        if (child + 1 <= heapSize && heap[child + 1] < heap[child]) child++;
        if (heap[i] < heap[child]) break;
        swap(&heap[i], &heap[child]); i = child;
    }
    return min;
}

void freeSlot(int slot) { insertHeap(slot); } // Free slot, make available  

void initHeap(int n) {
    // Initialize heap with 1...n slots  
    heapSize = 0;
    for (int i = 1; i <= n; i++) insertHeap(i);
}

//   Linked List for parked cars  
//  
typedef struct CarNode {
    char CarID[20];            // Plate or car ID  
    int SlotNo;                // Slot number assigned  
    int VIP;                   // Is it a VIP car?  
    time_t ArrivalTime;        // Arrival timestamp  
    time_t ExitTime;           // Exit timestamp  
    double Bill;               // Calculated bill  
    struct CarNode* next;      // Pointer to next node  
} CarNode;

CarNode* head = NULL; // Head of linked list for parked cars  

void insertCar(const char* carID, int slotNo, int vip) {
    // Add a new parked car  
    CarNode* newNode = (CarNode*)malloc(sizeof(CarNode));
    strcpy(newNode->CarID, carID);
    newNode->SlotNo = slotNo;
    newNode->VIP = vip;
    newNode->ArrivalTime = time(NULL);
    newNode->ExitTime = 0;
    newNode->Bill = 0.0;
    newNode->next = head; head = newNode;
    printf("Car %s parked in slot %d at %s", carID, slotNo, ctime(&newNode->ArrivalTime));
}

double calculateBill(CarNode* car) {
    // Compute bill based on parking duration and VIP status  
    double hours = difftime(car->ExitTime, car->ArrivalTime) / 3600.0;
    if (hours < 0.5) hours = 0.5; // Min. charge for 30 min  
    double rate = car->VIP ? 15.0 : 20.0;
    return hours * rate;
}

//   Remove Car + Bill + Time Info  
double removeCarWithBill(const char* carID, char* arrivalBuf, char* exitBuf) {
    // Remove car by ID, calculate bill, record exit info  
    CarNode* temp = head; CarNode* prev = NULL;
    while (temp) {
        if (strcmp(temp->CarID, carID) == 0) {
            temp->ExitTime = time(NULL); temp->Bill = calculateBill(temp);
            strftime(arrivalBuf, 50, "%Y-%m-%d %H:%M:%S", localtime(&temp->ArrivalTime));
            strftime(exitBuf, 50, "%Y-%m-%d %H:%M:%S", localtime(&temp->ExitTime));
            int slot = temp->SlotNo; double finalBill = temp->Bill;
            if (prev) prev->next = temp->next;
            else head = temp->next;
            freeSlot(slot); free(temp); return finalBill;
        }
        prev = temp; temp = temp->next;
    }
    return -1.0; // Car not found  
}

//   Queue for waiting cars (VIP handled)  
// 
typedef struct QueueNode {
    char CarID[20];
    int VIP;
    time_t ArrivalTime;
    struct QueueNode* next;
} QueueNode;

QueueNode* front = NULL; QueueNode* rear = NULL;

void enqueue(const char* carID, int vip) {
    // Add car to queue; VIP cars go to front  
    QueueNode* newNode = (QueueNode*)malloc(sizeof(QueueNode));
    strcpy(newNode->CarID, carID); newNode->VIP = vip;
    newNode->ArrivalTime = time(NULL); newNode->next = NULL;
    if (!front) { front = rear = newNode; return; }
    if (vip) { newNode->next = front; front = newNode; return; }
    rear->next = newNode; rear = newNode;
}

QueueNode* dequeue() {
    // Remove the earliest waiting car  
    if (!front) return NULL;
    QueueNode* temp = front; front = front->next;
    if (!front) rear = NULL; return temp;
}

//   Display Utility  
void displayParkedCars() {
    // Print list of all parked cars with details  
    CarNode* temp = head;
    printf("\n---- Parked Cars ----\n");
    while (temp) {
        printf("Car: %-10s | Slot: %2d | VIP: %d | Arrival: %s",
            temp->CarID, temp->SlotNo, temp->VIP, ctime(&temp->ArrivalTime));
        temp = temp->next;
    }
}
