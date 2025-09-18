import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  `${window.location.protocol}//${window.location.host}/api`;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(
      `Making ${config.method?.toUpperCase()} request to ${config.url}`
    );
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const uploadVideo = async (file, styleOptions) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("font_size", styleOptions.font_size);
  formData.append("font_family", styleOptions.font_family);
  formData.append("font_color", styleOptions.font_color);
  formData.append("highlight_color", styleOptions.highlight_color);
  formData.append("bottom_padding", styleOptions.bottom_padding);
  formData.append("word_mode", styleOptions.word_mode);

  console.log("Sending form data:", {
    file: file.name,
    font_size: styleOptions.font_size,
    font_family: styleOptions.font_family,
    font_color: styleOptions.font_color,
    highlight_color: styleOptions.highlight_color,
    bottom_padding: styleOptions.bottom_padding,
    word_mode: styleOptions.word_mode,
  });

  const response = await api.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    timeout: 300000, // 5 minutes timeout for video processing
  });

  return response.data;
};

// Debug function to test raw request
export const debugUpload = async (file, styleOptions) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("font_size", styleOptions.font_size);
  formData.append("font_family", styleOptions.font_family);
  formData.append("font_color", styleOptions.font_color);
  formData.append("highlight_color", styleOptions.highlight_color);
  formData.append("bottom_padding", styleOptions.bottom_padding);
  formData.append("word_mode", styleOptions.word_mode);

  const response = await api.post("/debug-upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const getStatus = async (taskId) => {
  const response = await api.get(`/status/${taskId}`);
  return response.data;
};

export const downloadVideo = async (taskId) => {
  const response = await api.get(`/download/${taskId}`, {
    responseType: "blob",
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `video_with_subtitles_${taskId}.mp4`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const downloadSubtitles = async (taskId) => {
  const response = await api.get(`/download/subtitles/${taskId}`, {
    responseType: "blob",
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `subtitles_${taskId}.srt`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const getStyles = async () => {
  const response = await api.get("/styles");
  return response.data;
};

export const cleanupTask = async (taskId) => {
  const response = await api.delete(`/cleanup/${taskId}`);
  return response.data;
};

export default api;
