#  Read summary_distances.dat.
def ReafFile():
    from pandas import read_csv

    data = read_csv('summary_distances.dat',sep=" ",header=None)
    data = data.sort_values(1,axis=0).values
    return data

#  Check if argument has been passed through command line.
def CheckArguments(argv,data):
    from sys import exit

    if (len(argv) < 2):
        print('Missing arguments.\n'
              'Add the step size, according to the size of\n'
              '\"summary distances.dat\" (for this file the size should be greater\n'
              'than 1) or distance between molecules (for this file the size should\n'
              'be less than 1), depending of the sampling method.\n'
             f'File \"summary distances.dat\" has {len(data)} data in it.\n'
             f'Minimum distance between molecules: {data[0,1].round(3)}.\n'
             f'Maximum distance between molecules: {data[-1,1].round(3)}.\n')
        exit('\nPROCESS INTERRUPTED')

#  Sort and sample data.
def SortAndSampleDAta(data):
    from numpy import array,empty,arange,append
    
    if float(argv[1]) >= 1:
        sampled_data = array([data[i,:] for i in range(0,len(data),int(argv[1]))])
    else:
        sampled_data = empty((0,2))
        for i in arange(data[0,1],data[-1,1],float(argv[1])):
            value = data[data[:,1] >= i]
            if value[0] not in sampled_data:
                sampled_data = append(sampled_data,[value[0]],axis=0)
    return sampled_data

# Write npt_pull.sh, md_pull.sh, tpr-files.dat and pullf-files.dat files
def WrittingFiles(sampled_data):
    from time import strftime,localtime

    #  Create string representing bash array.
    sample = 'sample=('
    for i in range(len(sampled_data)): sample += str(int(sampled_data[i,0]))+' '
    sample += ')'

    #  Write bash scripts.
    with open('npt_pull.sh','w') as npt:
        npt.write('#!/bin/bash\n'
                  '#######################################################################################################\n'
                  '# Authors: Diana Marlén Castañeda Bagatella and Santiago Alberto Flores Román.\n'
                 f'# Last edition: {strftime("%b %dth, %Y  %H:%M GTM%z",localtime())}.\n'
                  '# Description: This Bash script does umbrella sampling through GROMACS, running a sample\n'
                  '#              of system configurations (conf#.gro, where # is a number) generated previously.\n'
                  '#              Two files (npt_pull.sh and md_pull.sh) are needed to finish the sampling: The\n'
                  '#              first one runs the NPT equilibration over the respective configuration, whereas\n'
                  '#              the second one does the umbrella sampling using the output files generated by\n'
                  '#              the npt_pull.sh script.\n'
                  '#              Note that index.ndx, topol.top, npt_umbrella.mdp, md_umbrella.mdp and configuration\n'
                  '#              files must be in the same rute as Bash scripts to make this work.\n'
                  '# Instructions: Just execute them. Both files must be run in the order as they were mentioned above.\n'
                  '#\n'
                  '# Good luck! (if you believe in it).\n'
                  '#######################################################################################################\n\n'
                 f'{sample}\n'
                  'len_samples=${#sample[@]}\n\n'
                  'for (( i=0; i<${len_samples}; i++ ))\n'
                  'do\n'
                  '\tgmx grompp -f npt_umbrella.mdp -c conf${sample[${i}]}.gro -p topol.top -r conf${sample[${i}]}.gro -n index.ndx -o npt${i}.tpr -maxwarn 1\n'
                  'done\n'
                  'if [ $? -eq 0 ]\n'
                  'then\n'
                  '\tfor ((i=0; i<${len_samples}; i++))\n'
                  '\tdo\n'
                  '\t\tgmx mdrun -deffnm npt${i} -nb gpu\n'
                  '\tdone\n'
                  'fi\n')
    with open('md_pull.sh','w') as md:
        md.write('#!/bin/bash\n'
                 '#######################################################################################################\n'
                 '# Authors: Diana Marlén Castañeda Bagatella and Santiago Alberto Flores Román.\n'
                f'# Last edition: {strftime("%b %dth, %Y  %H:%M GTM%z",localtime())}.\n'
                 '# Description: This Bash script does umbrella sampling through GROMACS, running a sample\n'
                 '#              of system configurations (conf#.gro, where # is a number) generated previously.\n'
                 '#              Two files (npt_pull.sh and md_pull.sh) are needed to finish the sampling: The\n'
                 '#              first one runs the NPT equilibration over the respective configuration, whereas\n'
                 '#              the second one does the umbrella sampling using the output files generated by\n'
                 '#              the npt_pull.sh script.\n'
                 '#              Note that index.ndx, topol.top, npt_umbrella.mdp, md_umbrella.mdp and configuration\n'
                 '#              files must be in the same rute as Bash scripts to make this work.\n'
                 '# Instructions: Just execute them. Both files must be run in the order as they were mentioned above.\n'
                 '#\n'
                 '# Good luck! (if you believe in it).\n'
                 '#######################################################################################################\n\n'
                f'{sample}\n'
                 'len_samples=${#sample[@]}\n\n'
                 'for (( i=0; i<${len_samples}; i++ ))\n'
                 'do\n'
                 '\tgmx grompp -f md_umbrella.mdp -c npt${i}.gro -t npt${i}.cpt -p topol.top -r npt${i}.gro -n index.ndx -o umbrella${i}.tpr -maxwarn 1\n'
                 'done\n'
                 'if [ $? -eq 0 ]\n'
                 'then\n'
                 '\tfor ((i=0; i<${len_samples}; i++))\n'
                 '\tdo\n'
                 '\t\tgmx mdrun -deffnm umbrella${i} -nb gpu\n'
                 '\tdone\n'
                 'fi\n')

    # Write .dat files.
    with open('tpr-files.dat','w') as tprf:
        for i in range(len(sampled_data)): tprf.write(f'umbrella{i}.tpr\n')
    with open('pullf-files.dat','w') as pullf:
        for i in range(len(sampled_data)): pullf.write(f'umbrella{i}_pullf.xvg\n')

# Print Successful termination.
def SuccessfulProcess():
    # Print some output data.
    print('Files \"npt_pull.sh\" and \"md_pull.sh\" written.')
    print(f'Num. of samples collected: {len(sampled_data)}')
    print(f'        Samples collected: {sampled_data[:,1]}')
    print('\nSUCCESSFUL TERMINATION')

if __name__ == '__main__':
    from sys import argv

    data = ReafFile()
    CheckArguments(argv,data)
    sampled_data = SortAndSampleDAta(data)
    WrittingFiles(sampled_data)
    SuccessfulProcess()

