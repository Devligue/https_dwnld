This script allows to download file from user&password protected https url.

ORIGINAL FILE NAME:                                              https_dwnld.py

ARGUMENTS:                                                                    
Short:    Long:               Description:                      Status:        
-h        --help              show help for this script                optional
-u        --user              user name for url login                obligatory
-p        --password          password for url login                 obligatory
-f        --file_url          complete url to downloaded file        obligatory
-d        --save_directory    path to file save directory            obligatory
-o        --only_show         use to print instead of dwnld            optional
-s        --silent            use to hide progress bar                 optional

EXAMPLARY USAGE (from cmd line / terminal):

1. To download file to specified directory (short parameters):
> https_dwnld.py -u user -p pass -f url_to_file -d file_save_dir

2. To download file to specified directory (long parameters):
> https_dwnld.py --user user --password pass --file_url url_to_file
--save_directory file_save_dir

3. To print file text content /for text files only/ (short parameters):
> https_dwnld.py -u user -p pass -f url_to_file -d file_save_dir -o

4. To print file text content /for text files only/ (short parameters):
> https_dwnld.py --user user --password pass --file_url url_to_file
--save_directory file_save_dir --only_show

5. To do any of the above but w/o displaying progress bar in terminal add '-s'
or '--silent' just like:
> https_dwnld.py --user user --password pass --file_url url_to_file
--save_directory file_save_dir --only_show --silent

OUTPUT:
If everything worked fine script returns 'Completed' string to the console. If
option show_only was used script will return file text content string instead
of 'Completed' string. In case of any error an 'Error' string will be returned
with no additional information.
