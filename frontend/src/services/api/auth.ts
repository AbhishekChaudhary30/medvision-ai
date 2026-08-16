import { apiClient } from "./client";
import { User } from "./types";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const login = async (username: string, password: string):Promise<TokenResponse> => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  
  const { data } = await apiClient.post<TokenResponse>("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  
  localStorage.setItem("token", data.access_token);
  return data;
};

export const register = async (email: string, password: string):Promise<User> => {
  const { data } = await apiClient.post<User>("/auth/register", {
    email,
    password
  });
  return data;
};

export const logout = () => {
  localStorage.removeItem("token");
};

export const getMe = async (): Promise<User> => {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
};
