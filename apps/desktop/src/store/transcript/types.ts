import type { SpeakerHintStorage, WordStorage } from "@echonote/store";

export type WordWithId = WordStorage & { id: string };
export type SpeakerHintWithId = SpeakerHintStorage & { id: string };
