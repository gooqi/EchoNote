import type { PromptStorage } from "@echonote/store";
import type { Schemas } from "@echonote/store";

import type { Store } from "../../store/main";
import { createMarkdownDirPersister } from "../factories";
import { parsePromptIdFromPath } from "./changes";
import { frontmatterToPrompt, promptToFrontmatter } from "./transform";

export function createPromptPersister(store: Store) {
  return createMarkdownDirPersister<Schemas, PromptStorage>(store, {
    tableName: "prompts",
    dirName: "prompts",
    label: "PromptPersister",
    entityParser: parsePromptIdFromPath,
    toFrontmatter: promptToFrontmatter,
    fromFrontmatter: frontmatterToPrompt,
  });
}
