#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//Tamarica shaw
//620154865

void main(){
    char  kbinput[300];
    FILE *fptr;


    fptr= fopen("keylogfile.txt", "w");

    while (1)
    {
        system("echo $PS1");
        fgets(kbinput,sizeof(kbinput),stdin); 
        system(kbinput);
        fprintf(fptr,"%s",kbinput);
        
        if (strcmp(kbinput ,"~\n")==0){
            
            break;
        }

        }
    fclose(fptr);
    








}