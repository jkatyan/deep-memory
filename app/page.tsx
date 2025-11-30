"use client"

import { Button } from "@/components/ui/button";
import { Field, FieldError, FieldGroup, FieldLabel, FieldLegend, FieldSet } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { FormEvent } from "react";
import { useForm } from "@tanstack/react-form"
import * as z from "zod"
import { toast } from "sonner"
import { Toaster } from "@/components/ui/sonner";

export default function Home() {
  const router = useRouter()

  const formSchema = z.object({
    openAi: z
      .string()
      .nonempty(),
    // .length(43),
    pinecone: z
      .string()
      .nonempty(),
    // .length(75),
    awsAccess: z.string().nonempty(),
    awsSecret: z.string().nonempty(),
    awsBucketName: z.string().nonempty()
  })

  const form = useForm({
    defaultValues: {
      openAi: "",
      pinecone: "",
      awsAccess: "",
      awsSecret: "",
      awsBucketName: ""
    },
    validators: {
      onSubmit: formSchema,
    },
    onSubmit: async ({ value }) => {
      let response = await fetch("/api/credentials", { method: "POST", body: JSON.stringify(value) })
      let json = await response.json()
      console.log(json)
      if (json.statusCode == 200) {
        toast.success("Success! Routing to main app")
        localStorage.setItem("uuid", json["data"]["uuid"])
        router.push("/chat")
      }
      else {
        toast.error("Something went wrong. Please try again")
      }
    }
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    form.handleSubmit()
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
          </FieldSet>
          {
            form.Field({
              name: "openAi",
              children: (field) => {
                const isInvalid =
                  field.state.meta.isTouched && !field.state.meta.isValid

                return (
                  <Field data-invalid={isInvalid}>
                    <FieldLabel htmlFor={field.name}>
                      OpenAI API Key
                    </FieldLabel>
                    <Input
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      aria-invalid={isInvalid}
                      data-invalid={isInvalid ? "true" : undefined}
                      placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                      autoComplete="off"
                    />
                    {isInvalid && (
                      <FieldError errors={field.state.meta.errors} />
                    )}
                  </Field>
                );
              },
            })
          }

          {
            form.Field({
              name: "pinecone",
              children: (field) => {
                const isInvalid =
                  field.state.meta.isTouched && !field.state.meta.isValid

                return (
                  <Field data-invalid={isInvalid}>
                    <FieldLabel htmlFor={field.name}>
                      Pinecone API Key
                    </FieldLabel>
                    <Input
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      aria-invalid={isInvalid}
                      data-invalid={isInvalid ? "true" : undefined}
                      placeholder="pcsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                      autoComplete="off"
                    />
                    {isInvalid && (
                      <FieldError errors={field.state.meta.errors} />
                    )}
                  </Field>
                );
              },
            })
          }


          {
            form.Field({
              name: "awsAccess",
              children: (field) => {
                const isInvalid =
                  field.state.meta.isTouched && !field.state.meta.isValid

                return (
                  <Field data-invalid={isInvalid}>
                    <FieldLabel htmlFor={field.name}>
                      AWS Access Key
                    </FieldLabel>
                    <Input
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      aria-invalid={isInvalid}
                      data-invalid={isInvalid ? "true" : undefined}
                      autoComplete="off"
                    />
                    {isInvalid && (
                      <FieldError errors={field.state.meta.errors} />
                    )}
                  </Field>
                );
              },
            })
          }

          {
            form.Field({
              name: "awsSecret",
              children: (field) => {
                const isInvalid =
                  field.state.meta.isTouched && !field.state.meta.isValid

                return (
                  <Field data-invalid={isInvalid}>
                    <FieldLabel htmlFor={field.name}>
                      AWS Secret Key
                    </FieldLabel>
                    <Input
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      aria-invalid={isInvalid}
                      data-invalid={isInvalid ? "true" : undefined}
                      autoComplete="off"
                    />
                    {isInvalid && (
                      <FieldError errors={field.state.meta.errors} />
                    )}
                  </Field>
                );
              },
            })
          }

          {
            form.Field({
              name: "awsBucketName",
              children: (field) => {
                const isInvalid =
                  field.state.meta.isTouched && !field.state.meta.isValid

                return (
                  <Field data-invalid={isInvalid}>
                    <FieldLabel htmlFor={field.name}>
                      AWS Bucket Name
                    </FieldLabel>
                    <Input
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      aria-invalid={isInvalid}
                      data-invalid={isInvalid ? "true" : undefined}
                      autoComplete="off"
                    />
                    {isInvalid && (
                      <FieldError errors={field.state.meta.errors} />
                    )}
                  </Field>
                );
              },
            })
          }

          <Field orientation="horizontal">
            <Button type="submit">Submit</Button>
          </Field>
        </FieldGroup>
      </form>

      <Toaster />
    </main>
  )
}
