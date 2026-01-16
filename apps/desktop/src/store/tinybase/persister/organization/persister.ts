import type { OrganizationStorage } from "@echonote/store";
import type { Schemas } from "@echonote/store";

import type { Store } from "../../store/main";
import { createMarkdownDirPersister } from "../factories";
import { parseOrganizationIdFromPath } from "./changes";
import {
  frontmatterToOrganization,
  organizationToFrontmatter,
} from "./transform";

export function createOrganizationPersister(store: Store) {
  return createMarkdownDirPersister<Schemas, OrganizationStorage>(store, {
    tableName: "organizations",
    dirName: "organizations",
    label: "OrganizationPersister",
    entityParser: parseOrganizationIdFromPath,
    toFrontmatter: organizationToFrontmatter,
    fromFrontmatter: frontmatterToOrganization,
  });
}
