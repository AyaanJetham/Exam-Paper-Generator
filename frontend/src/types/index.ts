export interface Resource {
    title: string;
    link: string;
    snippet: string;
    relevance_score: number;
  }
  
  export interface Course {
    id: string;
    title: string;
    instructors: string;
    duration: string;
    url: string;
    similarity: number;
  }
  