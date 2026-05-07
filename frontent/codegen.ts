import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: "http://localhost:8001/graphql", // reads schema from your live API
  documents: ["app/**/*.tsx", "app/**/*.ts"],
  generates: {
    "./app/__generated__/": {
      preset: "client",
    },
  },
};

export default config;
