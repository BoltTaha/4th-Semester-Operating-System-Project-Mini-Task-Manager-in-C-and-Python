#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h> 
#include <pthread.h>
#include <semaphore.h>
#include <sys/resource.h>
#include <sys/sysinfo.h>

void export_processes_to_file(void);
int kill_process(int pid);
void list_threads(int pid);


// Define ProcessInfo struct
typedef struct {
    int pid;
    char name[256];
    int priority;
    long memory;
    float cpu_usage;
} ProcessInfo;

// Max number of processes to track
#define MAX_PROCESSES 1024

// Global process list
ProcessInfo processes[MAX_PROCESSES];
int process_count = 0;

// Semaphore to protect access to processes[]
sem_t mutex;

long long get_total_cpu_time() {
    FILE *fp = fopen("/proc/stat", "r");
    if (!fp) return -1;

    char cpu[5];
    long user, nice, system, idle, iowait, irq, softirq, steal;
    fscanf(fp, "%s %ld %ld %ld %ld %ld %ld %ld %ld", cpu, &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal);
    fclose(fp);

    return (long long)(user + nice + system + idle + iowait + irq + softirq + steal);
}


long long get_process_cpu_time(int pid) {
    char path[64];
    sprintf(path, "/proc/%d/stat", pid);
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;

    long utime, stime;
    int i;
    char buffer[1024];
    fgets(buffer, sizeof(buffer), fp);
    fclose(fp);

    char *token = strtok(buffer, " ");
    for (i = 1; i <= 13; i++) token = strtok(NULL, " "); // skip to utime
    utime = atol(strtok(NULL, " "));
    stime = atol(strtok(NULL, " "));

    return utime + stime;
}


//-----------------------------------------------------------------------

void get_process_list() 
{
    long long total_time_before = get_total_cpu_time();
    long long proc_time_before[MAX_PROCESSES];

    sem_wait(&mutex);
    process_count = 0;

    DIR *dir = opendir("/proc");
    if (!dir) 
    { 
        perror("opendir /proc"); 
        sem_post(&mutex); 
        return; 
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) 
    {
    if (isdigit(*entry->d_name)) 
       {
       
        int pid = atoi(entry->d_name);
        char path[256], line[512];
        FILE *fp;

        sprintf(path, "/proc/%d/comm", pid);
        fp = fopen(path, "r");
        if (!fp) continue;
        fgets(processes[process_count].name, 256, fp);
        processes[process_count].name[strcspn(processes[process_count].name, "\n")] = 0;
        fclose(fp);

        processes[process_count].pid = pid;

        // Memory
        sprintf(path, "/proc/%d/status", pid);
        fp = fopen(path, "r");
        if (!fp) continue;
        while (fgets(line, sizeof(line), fp)) 
        {
            if (strncmp(line, "VmRSS:", 6) == 0) 
            {
                sscanf(line + 6, "%ld", &processes[process_count].memory);
                break;
            }
        }
        
        fclose(fp);

        processes[process_count].priority = getpriority(PRIO_PROCESS, pid);
        proc_time_before[process_count] = get_process_cpu_time(pid);

        process_count++;
        if (process_count >= MAX_PROCESSES) break;
    }
}

closedir(dir);
sem_post(&mutex);

// Wait a moment to calculate CPU usage delta
usleep(1000000); // (a second)


long long total_time_after = get_total_cpu_time();

sem_wait(&mutex);
int num_cores = get_nprocs(); // include <sys/sysinfo.h>
long ticks_per_sec = sysconf(_SC_CLK_TCK); // include <unistd.h>

for (int i = 0; i < process_count; i++) 
{
    long long proc_time_after = get_process_cpu_time(processes[i].pid);
    long long proc_delta = proc_time_after - proc_time_before[i];
    long long total_delta = total_time_after - total_time_before;

    if (total_delta > 0 && ticks_per_sec > 0) 
    {
        // Normalize: get percentage CPU usage over interval, accounting for all CPU cores
        processes[i].cpu_usage = 100 * ((double)proc_delta / total_delta) * num_cores;
    } else {
        processes[i].cpu_usage = 0.0;
    }
}

sem_post(&mutex);

}


//  -----------------------------------------------------------------


void *refresh_thread(void *arg) {
    while (1) {
        get_process_list();          // Update process list
        export_processes_to_file();  // Dump to file
        sleep(1);                    // Every 1 second
    }
    return NULL;
}


// -----------------------------------------------------------------

void export_processes_to_file() {
    sem_wait(&mutex);
    FILE *fp = fopen("process_data.txt", "w");
    if (!fp) {
        perror("fopen process_data.txt");
        sem_post(&mutex);
        return;
    }

    for (int i = 0; i < process_count; i++) {
        fprintf(fp, "%d,%s,%d,%ld,%.2f\n",
            processes[i].pid,
            processes[i].name,
            processes[i].priority,
            processes[i].memory,
            processes[i].cpu_usage
        );
    }

    fclose(fp);
    sem_post(&mutex);
}


//---------------------------------------------------------------------



int kill_process(int pid) 
{
   char path[64];
    sprintf(path, "/proc/%d", pid);

    // Try opening the directory for the process
    DIR *dir = opendir(path);
    if (!dir) 
    {
       
        printf("Process %d does not exist.\n", pid);
        return -1;
    }

    
    closedir(dir);

    
    int result = kill(pid, SIGKILL);
    if (result == 0) 
        printf("Process %d killed successfully.\n", pid);
     else 
        perror("Failed to kill process");
    
    return result;

}


//----------------------------------------------------------------------


void list_threads(int pid) {
    char path[64];
    sprintf(path, "/proc/%d/task", pid);

    DIR *dir = opendir(path);
    if (!dir) {
        perror("Could not open task directory");
        return;
    }

    struct dirent *entry;
    printf("Threads for PID %d:\n", pid);

    while ((entry = readdir(dir)) != NULL) {
        if (!isdigit(*entry->d_name))
            continue;

        // Thread ID
        char *tid = entry->d_name;

        // Optional: Get thread name from comm
        char comm_path[128];
        sprintf(comm_path, "/proc/%d/task/%s/comm", pid, tid);
        FILE *fp = fopen(comm_path, "r");
        char thread_name[256] = "Unknown";
        if (fp) {
            fgets(thread_name, sizeof(thread_name), fp);
            thread_name[strcspn(thread_name, "\n")] = 0;
            fclose(fp);
        }

        printf("  Thread ID: %s (%s)\n", tid, thread_name);
    }

    closedir(dir);
}



// ------------------------------------------------------------------

void print_process_list() {
    sem_wait(&mutex);
    printf("%-8s %-25s %-8s %-10s %s\n",
           "PID", "Name", "Prio", "Memory(KB)", "CPU%");
    for (int i = 0; i < process_count; i++) {
        printf("%-8d %-25s %-8d %-10ld %.2f\n",
               processes[i].pid,
               processes[i].name,
               processes[i].priority,
               processes[i].memory,
               processes[i].cpu_usage);
    }
    sem_post(&mutex);
}


//-----------------------------------------------------------------------


int main(int argc, char *argv[]) {
    pthread_t tid;
    sem_init(&mutex, 0, 1);
    pthread_create(&tid, NULL, refresh_thread, NULL);

    // Test mode
    if (argc > 1 && strcmp(argv[1], "--test") == 0) {
        sleep(1);
        get_process_list();
        print_process_list();
        goto cleanup;
    }

    // List threads of a process
    if (argc > 2 && strcmp(argv[1], "--threads") == 0) {
        int pid = atoi(argv[2]);
        list_threads(pid);
        goto cleanup;
    }

    // Kill a process by PID
    if (argc == 2) {
        int pid = atoi(argv[1]);
        kill_process(pid);
        goto cleanup;
    }

    // Interactive CLI mode
    int choice, pid;
    while (1) {
        printf("\n1. Kill a process\n2. List threads of a process\n3. Exit\nChoose: ");
        scanf("%d", &choice);

        if (choice == 1) {
            printf("Enter PID to kill: ");
            scanf("%d", &pid);
            kill_process(pid);
        } else if (choice == 2) {
            printf("Enter PID to list threads: ");
            scanf("%d", &pid);
            list_threads(pid);
        } else if (choice == 3) {
            break;
        }
    }

cleanup:
    pthread_cancel(tid);
    pthread_join(tid, NULL);
    sem_destroy(&mutex);
    return 0;
}
