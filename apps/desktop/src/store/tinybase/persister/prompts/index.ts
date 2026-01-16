import * as _UI from "tinybase/ui-react/with-schemas";

import { getCurrentWebviewWindowLabel } from "@echonote/plugin-windows";
import { type Schemas } from "@echonote/store";

import type { Store } from "../../store/main";
import { createPromptPersister } from "./persister";

const { useCreatePersister } = _UI as _UI.WithSchemas<Schemas>;

export function usePromptPersister(store: Store) {
  return useCreatePersister(
    store,
    async (store) => {
      const persister = createPromptPersister(store as Store);
      if (getCurrentWebviewWindowLabel() === "main") {
        await persister.startAutoPersisting();
      } else {
        await persister.startAutoLoad();
      }
      return persister;
    },
    [],
  );
}
