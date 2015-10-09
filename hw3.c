/* third homework, you will use C to implement a fork-based calculator program. The goal is
to work with pipes and processes, i.e., inter-process communication (IPC) */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <assert.h>
#include <ctype.h>

#define OPLENGTH  10000 
#define DEBUG

int words(const char sentence[ ])
{
    int counted = 0; // result

    // state:
    const char* it = sentence;
    int inword = 0;

    do switch(*it) {
        case '\0': 
        case ' ': case '\t': case '\n': case '\r': // TODO others?
            if (inword) { inword = 0; counted++; }
            break;
        default: inword = 1;
    } while(*it++);

    return counted;
} 

int func(char * str, int reportPipe)
{
#ifndef DEBUG
  printf("PROCESS %d: start with: %s\n", getpid(), str);
#endif

  int start = 0;
  char * level[OPLENGTH]; 
  int cap = 0;

  if(str[0]=='(' && strlen(str)>3 ){
    if(str[1]!='+' && str[1]!='-' && str[1]!='*' && str[1]!='/'){
      int xx = 1;
      for(;xx<strlen(str) && str[xx]!=' ';xx++){
      }
      char tmp[OPLENGTH];
      strncpy(tmp, str+1, xx-1);
      printf("PROCESS %d: ERROR: unknown \'%s\' operator\n", getpid(), tmp);
      exit(-1);
    }

    if(words(str)<3){
      printf("PROCESS %d: ERROR: not enough operands\n", getpid());
      exit(-1);
    }

    start = 3;
  }
  else{
#ifndef DEBUG
    printf("PROCESS %d: one char: %d\n", getpid(), atoi(str));
#endif
    return atoi(str);
    exit(0);
  }

  //@TODO Split the expression
  int flag = start;
  int i = start;
  char * buffer = NULL;
  int bracket = 0;

  for(; i<strlen(str); i++)
  {
    if((str[i]==' '||str[i]==')')&& bracket==0)
    { 
      buffer = calloc(i-flag+1, sizeof(char));
      strncpy(buffer, str+flag, i-flag); 

      level[cap++] = buffer;
    }
    else if(str[i]=='('){
      bracket++;
    }
    else if(str[i]==')'){
      bracket--;
    }

    if(str[i]==' ' && bracket==0){
      flag = i+1;
    }
  }
  
  char op = str[1];
#ifndef DEBUG
  printf("PROCESS %d: op=%c cap=%d in %s\n", getpid(), op, cap, str);
#endif

  printf("PROCESS %d: Starting \'%c\' operation\n", getpid(), op);

  int p[cap][2];  /* array to hold the two pipe file descriptors
                  (p[0] is the read end; p[1] is the write end) */

  int s;
  pid_t pid;     /* process id (pid)  unsigned int/short */
  int rc = -1;
  for(s = 0; s < cap; s++)
  {
    rc = pipe( p[s] );

    if ( rc == -1 )
    {
      perror( "pipe() failed" );
      exit(-1);
      return EXIT_FAILURE;
    }

    pid = fork();  /* create a child process */
  
    if ( pid == -1 )
    {
      perror( "fork() failed" );
      exit(-1);
      return EXIT_FAILURE;
    }
    if ( pid == 0 )  /* child process fork() returns 0 */
    {
      close( p[s][0] );
      //printf("PROCESS %d: I am on %s\n", getpid(), opStr);
      int value = func(level[s], p[s][1]);
      //printf("PROCESS %d: xreturns: %d\n", getpid(), value);
      write( p[s][1], &value, sizeof(value));
      printf("PROCESS %d: Sending \'%d\' on pipe to parent\n", getpid(), value);
      exit(0);
      return EXIT_SUCCESS;
    }
  }

  int r = cap-1;
  int rvalue;
  int result[OPLENGTH];
  int resultCap = 0;
  while(r>=0)
  {
    close( p[r][1] );  /* close the write end of the pipe */
    p[r][1] = -1;

    read( p[r][0], &rvalue, sizeof(rvalue) );   /* BLOCKING */
    //printf( "PARENT %d: Read %d bytes: %d\n", getpid(), bytes_read, rvalue);
    result[resultCap++] = rvalue;

    int status;
    //@TODO read pipe here
    pid_t child_pid = wait( &status );
  
    if ( WIFSIGNALED( status ) )   /* core dump or kill or kill -9 */
    {
      printf( "PARENT: child %d terminated ", (int)child_pid );
      printf( "abnormally\n" );
    }
    else if ( WIFEXITED( status ) ) /* child called return or exit() */
    {
      int rc = WEXITSTATUS( status );
      if(rc != 0){
        printf("PARENT: child %d terminated with nonzero exit status %d\n", (int)child_pid, rc );
        exit(-1); //note, here, there might be zombie processes
      }
    }

    --r;
  }

  //summarize child processes and write to parent

  int resulti = resultCap-2;
  int value = result[resultCap-1];
  while(resulti>=0){
    if(op=='+')
      value = (int)(value + result[resulti]);
    if(op=='-')
      value = (int)(value - result[resulti]);
    if(op=='*')
      value = (int)(value * result[resulti]);
    if(op=='/')
      value = (int)(value / result[resulti]);
    --resulti;
  }

  if(reportPipe != -1){
    write( reportPipe, &value, sizeof(value));
    printf("PROCESS %d: Sending \'%d\' on pipe to parent\n", getpid(), value);
    exit(0);
  }
  else{
    printf("PROCESS %d: Final answer is \'%d\'\n", getpid(), value);
  }
  return -1;
};

int main(int argc, char *argv[])
{ 
  if(argc != 2){
    printf("ERROR: Invalid arguments\nUSAGE: ./a.out <input-file>\n");
    return EXIT_FAILURE;
  }
   
  char name[80];
  strcpy( name, argv[1]);
  int fd = open( name, O_RDONLY );

  if ( fd == -1 )
  {
    perror( "open() failed" );
    return EXIT_FAILURE;
  }
  FILE * fp;
  char * line = NULL;
  char * opline = NULL;
  size_t len = 0;
  ssize_t read;

  fp = fopen(name, "r");
  if (fp == NULL)
  {
    perror( "read file failed" );
    return EXIT_FAILURE;
  }
  while ((read = getline(&line, &len, fp)) != -1)
  {
    if(line != NULL  && read >= 1)
    {
      if(line[0]!='#')
      {
        opline = (char *)calloc(len + 1, sizeof(char)); 
	strcpy(opline, line);
      }
    }
  }
  fclose(fp);

  //printf("%s", opline); 

  if(strlen(opline)<3 || opline[0]!='(')
  {
    printf("PROCESS %d: ERROR: not enough operands\n", getpid());
    exit(-1);
  }

  func(opline, -1);
  return EXIT_SUCCESS;
}
