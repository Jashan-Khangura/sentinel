import assert from "node:assert/strict";
import { resolve } from "node:path";

import postcss from "postcss";
import tailwindcss from "tailwindcss";
import loadConfig from "tailwindcss/loadConfig";
import { describe, expect, it, vi } from "vitest";

import {
  channelUiContribution,
  channelUiOwner,
  channelUiPresentation,
  registeredChannelUiContributions,
} from "@/channel-plugins/registry";

describe("channel UI contributions", () => {
  it("registers the Discord UI only through its backend manifest entry", () => {
    expect(channelUiContribution("discord", "webui/index.ts")?.presentation.displayName).toBe("Discord");
    expect(channelUiContribution("discord", undefined)).toBeUndefined();
    expect(channelUiContribution("discord", "webui/missing.tsx")).toBeUndefined();
    expect(channelUiContribution("missing", "webui/index.tsx")).toBeUndefined();

    const registrations = registeredChannelUiContributions();
    const channels = registrations.map((entry) => entry.channel);
    expect(channels).toEqual(["discord"]);
    expect(new Set(channels).size).toBe(channels.length);
    expect(registrations.every((entry) => /^webui\/index\.tsx?$/.test(entry.webui))).toBe(true);
    expect(channelUiPresentation("discord")?.displayName).toBe("Discord");
    expect(channelUiOwner("discord")).toBe("discord");
  });

  it("includes channel-owned UI in Tailwind's production scan", async () => {
    vi.stubEnv("NODE_ENV", "production");
    try {
      const config = loadConfig(resolve(process.cwd(), "tailwind.config.js"));
      assert(Array.isArray(config.content));
      // Keep production channel globs and exclusions without rebuilding unrelated app/test CSS.
      const content = config.content.filter((entry) => typeof entry === "string"
        && (entry.includes("../nanobot/channels/") || entry.startsWith("!")));
      const result = await postcss([tailwindcss({ ...config, content })]).process("@tailwind utilities;", { from: undefined });

      let objectFit: string | undefined;
      result.root.walkRules(".object-contain", (rule) => {
        rule.walkDecls("object-fit", (declaration) => {
          objectFit = declaration.value;
        });
      });
      expect(objectFit).toBe("contain");
    } finally {
      vi.unstubAllEnvs();
    }
  });
});
