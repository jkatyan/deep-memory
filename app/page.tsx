"use client"

import { Button } from "@/components/ui/button";
import { Field, FieldDescription, FieldError, FieldGroup, FieldLabel, FieldLegend, FieldSet } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { FormEvent } from "react";

export default function Home() {
  const router = useRouter()

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    router.push("/chat");
  }


  return (
    <main className="flex flex-col justify-center items-center h-screen dark:bg-black">
      <form
        className="flex flex-col justify-center w-1/2"
        onSubmit={handleSubmit}
      >
        <FieldGroup>
          <FieldSet>
            <FieldLegend>Deep Memory Setup</FieldLegend>
            <FieldDescription>
              All keys are stored in local storage and only used when necessary
            </FieldDescription>
          </FieldSet>
          <Field>
            <FieldLabel htmlFor="openapi-7j9-api-key-43j">
              OpenAI API Key
            </FieldLabel>
            <Input
              id="openapi-7j9-api-key-43j"
              placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              required
            />
            <FieldError />
          </Field>

          <Field>
            <FieldLabel htmlFor="pinecone-9qr-api-key-71z">
              Pinecone API Key
            </FieldLabel>
            <Input
              id="pinecone-9qr-api-key-71z"
              placeholder="pcsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              required
            />
          </Field>

          <Field>
            <FieldLabel htmlFor="aws-w7r-access-key-k6u">
              AWS Access Key
            </FieldLabel>
            <Input
              id="aws-w7r-access-key-k6u"
              required
            />
          </Field>

          <Field>
            <FieldLabel htmlFor="aws-h4n-secret-access-key-z1c">
              AWS Secret Key
            </FieldLabel>
            <Input
              id="aws-h4n-secret-access-key-z1c"
              required
            />
          </Field>

          <Field>
            <FieldLabel htmlFor="aws-r9t-bucket-name-m7b">
              AWS Bucket Name
            </FieldLabel>
            <Input
              id="aws-r9t-bucket-name-m7b"
              required
            />
          </Field>

          <Field orientation="horizontal">
            <Button type="submit">Submit</Button>
          </Field>
        </FieldGroup>
      </form>
    </main>
  )
}
