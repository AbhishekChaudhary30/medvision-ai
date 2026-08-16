import { User } from "./types";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const login = async (username: string, password: string):Promise<TokenResponse> => {
  // MOCK LOGIN FOR SERVERLESS REACT APP
  const token = "mock-token-" + Date.now();
  localStorage.setItem("token", token);
  return { access_token: token, token_type: "bearer" };
};

export const register = async (email: string, password: string):Promise<User> => {
  // MOCK REGISTER
  return {
    id: "user_mock",
    email: email,
    is_active: true,
    role: "USER"
  };
};

export const logout = () => {
  localStorage.removeItem("token");
};

export const getMe = async (): Promise<User> => {
  // MOCK GET ME
  return {
    id: "user_mock",
    email: "demo@medvision.ai",
    is_active: true,
    role: "ADMIN"
  };
};
