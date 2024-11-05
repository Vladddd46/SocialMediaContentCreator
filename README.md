<h2>Overview</h2>
autoContentCreator is application, which automatically creates and uploads content in social medias. For example, it downloads video-interview from youtube, cuts this video into highlights (also adds some filters if needed) and uploads these highlights to tiktok account. Which videos to download, how to process them and where to upload can be configured in configuration files, which are located in ./configurations folder.<br>

<h2>Quick start</h2>
>python3.12 -m venv env<br>
>source env/bin/activate<br>
>pip install -r requirements.txt<br>
# add your configurations to files in ./configurations. See how to configure the project in tutorils in ./docs folder<br>
>python main.py<br><br>
Note, that python3.12 should be used because some of the used modules are supported only for this python version.<br>

<h2>Directory Structure</h2>
1. ./configurations - contains configuration files.<br>
2. ./docs - documentation files.<br>
3. ./drafts - code snippets, which are used in the project.<br>
4. ./logs - log files.<br>
5. ./src - source code.<br>
6. ./accounts_data - automatically created folder, that is used for storing accounts data like content to upload, credentials, etc.<br>

<h2>Other</h2>
1. In todo_list.txt you may find tasks, which should be done.<br>
2. You can see how to format code in ./docs/how_to_format_files.txt file.<br>
3. To clean project directory from file, that were created during program excecution run:<br>
&nbsp;&nbsp;&nbsp;&nbsp;a. python main.py --clean<br>
&nbsp;&nbsp;&nbsp;&nbsp;b. python main.py --full_clean<br>