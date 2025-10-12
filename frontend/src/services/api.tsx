import axios from 'axios';
import { Resource } from '../types';

const API_URL = 'http://localhost:8000'; 
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadPDF = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getCourses = async () => {
  const response = await api.post('/get_courses');
  return response.data;
};

export const getResources = async (): Promise<Resource[]> => {
  const response = await api.post('/get_resources');
  return response.data.resources;
};

export const uploadQuestionPaper = async (formData: FormData) => {
  const response = await axios.post(`${API_URL}/upload-question-paper`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

