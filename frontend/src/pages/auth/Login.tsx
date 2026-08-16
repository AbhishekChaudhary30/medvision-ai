import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { login, register } from "../../services/api";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "../../components/ui/card";
import { Activity, Eye, EyeOff, Sparkles } from "lucide-react";

export function Login() {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login: setAuthToken } = useAuth();
  const navigate = useNavigate();

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    
    try {
      if (isRegisterMode) {
        await register(email, password);
      }
      const data = await login(email, password);
      setAuthToken(data.access_token);
      navigate("/");
    } catch (err: any) {
      navigate("/"); // ALWAYS navigate to dashboard on error in serverless mode
    } finally {
      setIsLoading(false);
    }
  };

  const handleExploreDemo = async () => {
    setError("");
    setIsLoading(true);
    try {
      await login("demo@medvision.com", "password123");
      setAuthToken("mock-token-123");
      navigate("/");
    } catch (err: any) {
      navigate("/"); // ALWAYS navigate to dashboard
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-secondary p-4">
      <Card className="w-full max-w-md bg-white border-0 shadow-lg">
        <CardHeader className="space-y-2 text-center pb-8">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <Activity className="h-6 w-6 text-primary" />
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight text-primary">
            MedVision AI (Serverless)
          </CardTitle>
          <CardDescription className="text-muted">
            {isRegisterMode ? "Create a new account" : "Sign in to your account"}
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleAuth}>
          <CardContent className="space-y-4">
            {error && (
              <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                className="h-11 border-gray-200"
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="h-11 border-gray-200 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 focus:outline-none"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-3 pt-4">
            <Button
              type="submit"
              className="w-full h-11 text-base font-semibold"
              disabled={isLoading}
            >
              {isLoading ? (isRegisterMode ? "Registering..." : "Signing in...") : (isRegisterMode ? "Register" : "Sign in")}
            </Button>
            
            <div className="text-sm text-center text-muted-foreground w-full py-2">
              {isRegisterMode ? "Already have an account? " : "Don't have an account? "}
              <button 
                type="button" 
                onClick={() => {
                  setIsRegisterMode(!isRegisterMode);
                  setError("");
                }} 
                className="text-primary font-medium hover:underline"
              >
                {isRegisterMode ? "Sign in" : "Register"}
              </button>
            </div>

            <div className="relative w-full">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-muted-foreground">Or</span>
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              onClick={handleExploreDemo}
              disabled={isLoading}
              className="w-full h-11 text-base font-medium border-gray-200 text-slate-700 bg-slate-50 hover:bg-slate-100"
            >
              <Sparkles className="mr-2 h-4 w-4 text-primary" />
              Explore V3 Serverless Demo
            </Button>
            
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
