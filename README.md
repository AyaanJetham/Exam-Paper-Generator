## EduResourceHub

EduResourceHub is a streamlined platform designed to connect users with the most relevant NPTEL courses and online resources based on their uploaded syllabus. It employs natural language processing and vector similarity to recommend educational materials tailored to user needs.

### Features

- Matches the uploaded syllabus to relevant NPTEL courses and displays them.
- Ranks and displays the most relevant learning resources based on syllabus keywords.

### Installation

1) Clone the repository:
   
   ``` bash
   https://github.com/Khan-Ramsha/EduResourceHub.git
   ```
   ``` bash
       cd EduResourceHub
   ```
2) Run the setup script:
   ``` bash
     chmod +x setup.sh
    ./setup.sh
   ```
   and for frontend  `npm install`
   
3) Create .env file and add your google custom search api keys from the Google Cloud Console, create a Custom Search Engine (CSE) at Google Custom Search add in the code `backend/src/getResources/search.py`.

### Usage

1) Run the frontend using `npm run dev`, Run the backend using `python backend/src/app.py`.
2) View the app at `http://localhost:5173`
3) Drop your syllabus PDF into the app.
4) Click on Get Courses to discover tailored courses based on your syllabus Or, hit Get Resources to explore relevant learning resources.
5) The UI will dynamically display exactly what you need, making it easier to get started on your learning journey.

### License
This project is licensed under the MIT License - see the [License](https://github.com/Khan-Ramsha/EduResourceHub/blob/main/LICENSE) file for details.
