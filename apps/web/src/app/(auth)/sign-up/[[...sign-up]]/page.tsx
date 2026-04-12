import { redirect } from "next/navigation";

// Mock mode: skip sign-up
export default function SignUpPage() {
  redirect("/dashboard");
}
