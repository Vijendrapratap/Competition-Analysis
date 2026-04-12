import { redirect } from "next/navigation";

// Mock mode: skip sign-in
export default function SignInPage() {
  redirect("/dashboard");
}
