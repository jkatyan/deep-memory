import { NextResponse } from "next/server";

export async function GET(request: Request) {
  return NextResponse.json({ messsage: "Hello World" });
}

export async function POST(request: Request) {
  const formData = request.formData

  return NextResponse.json({ text: "Ok", status: 200 });
}
