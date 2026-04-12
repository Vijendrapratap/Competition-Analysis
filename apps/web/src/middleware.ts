// Auth disabled in dev (no Clerk keys) — passthrough all routes
import { NextResponse } from "next/server";
export default function middleware() {
  return NextResponse.next();
}
export const config = { matcher: [] };
