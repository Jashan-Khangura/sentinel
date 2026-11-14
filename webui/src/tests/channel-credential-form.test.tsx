import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import {
  CredentialForm,
  channelValuesForSubmit,
  defaultChannelFieldValues,
} from "@/components/settings/channels/CredentialForm";
import { channelSetup } from "@/components/settings/channels/ChannelIdentity";
import type { ChannelConfigField } from "@/channel-plugins/catalog";

const fields: ChannelConfigField[] = [
  {
    key: "channels.discord.token",
    label: "Bot token",
    secret: true,
  },
  {
    key: "channels.discord.groupPolicy",
    label: "Group behavior",
    options: [
      { value: "mention", label: "Mention only" },
      { value: "open", label: "All messages" },
    ],
  },
];

describe("CredentialForm", () => {
  it("preserves inherited notices and lets an explicit override return to the default", () => {
    const key = "channels.discord.showCompactionNotices";
    const setup = channelSetup({
      name: "discord", display_name: "Discord", type: "channel", enabled: false,
      installed: true, ready: false, status: "not_enabled",
      install_supported: true, requires_restart: false,
      setup: { fields: [{
        key, field: "showCompactionNotices", kind: "bool", choices: [],
        required: false, inheritable: true,
      }] },
    });
    const noticeFields = setup.fields!;
    expect(defaultChannelFieldValues(noticeFields)).toEqual({ [key]: "" });
    expect(channelValuesForSubmit(noticeFields, {}, new Set())).toEqual({});
    expect(defaultChannelFieldValues(noticeFields, { [key]: "false" })).toEqual({ [key]: "false" });
    expect(channelValuesForSubmit(noticeFields, { [key]: "true" }, new Set([key])))
      .toEqual({ [key]: "true" });
    expect(channelValuesForSubmit(noticeFields, { [key]: "" }, new Set([key])))
      .toEqual({ [key]: "" });

    const onChange = vi.fn();
    render(<CredentialForm fields={noticeFields} values={{ [key]: "false" }}
      visibleSecrets={{}} onChange={onChange} onToggleSecret={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "Off" })).toBeChecked();
    fireEvent.click(screen.getByRole("radio", { name: "Default" }));
    expect(onChange).toHaveBeenCalledWith(key, "");
  });

  it("renders Discord proxy configuration as a switch and submits both boolean states", () => {
    const channel = "discord";
    const key = `channels.${channel}.useProxy`;
    const setup = channelSetup({
      name: channel, display_name: channel, type: "channel", enabled: true,
      webui: "webui/index.ts",
      installed: true, ready: true, status: "enabled",
      install_supported: true, requires_restart: false,
      setup: { fields: [{ key, field: "use_proxy", kind: "bool", choices: [], required: false, default_value: "false" }] },
    });
    const proxyFields = [...setup.fields ?? [], ...setup.manualFields ?? []];
    expect(proxyFields[0].section).toBe("connection");
    const onChange = vi.fn();
    const { rerender } = render(<CredentialForm fields={proxyFields} values={{ [key]: "true" }}
      visibleSecrets={{}} onChange={onChange} onToggleSecret={vi.fn()} />);
    const useProxy = screen.getByRole("switch", { name: "Use proxy" });
    expect(useProxy).toBeChecked();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    fireEvent.click(useProxy);
    expect(onChange).toHaveBeenCalledWith(key, "false");
    expect(channelValuesForSubmit(proxyFields, { [key]: "false" }, new Set([key]))).toEqual({ [key]: "false" });
    rerender(<CredentialForm fields={proxyFields} values={{ [key]: "false" }}
      visibleSecrets={{}} onChange={onChange} onToggleSecret={vi.fn()} />);
    fireEvent.click(screen.getByRole("switch", { name: "Use proxy" }));
    expect(onChange).toHaveBeenLastCalledWith(key, "true");
  });

  it("uses native radio semantics for option fields", () => {
    const onChange = vi.fn();
    render(
      <CredentialForm
        fields={[fields[1]!]}
        values={{ "channels.discord.groupPolicy": "mention" }}
        visibleSecrets={{}}
        onChange={onChange}
        onToggleSecret={vi.fn()}
      />,
    );

    const group = screen.getByRole("group", { name: "Group behavior" });
    expect(within(group).getByRole("radio", { name: "Mention only" })).toBeChecked();
    fireEvent.click(within(group).getByRole("radio", { name: "All messages" }));
    expect(onChange).toHaveBeenCalledWith("channels.discord.groupPolicy", "open");
  });

  it("associates option errors and exposes a stable focus target", () => {
    render(
      <CredentialForm
        fields={[fields[1]!]}
        values={{ "channels.discord.groupPolicy": "mention" }}
        visibleSecrets={{}}
        onChange={vi.fn()}
        onToggleSecret={vi.fn()}
        errors={{ "channels.discord.groupPolicy": "Required to complete setup." }}
      />,
    );

    const group = screen.getByRole("group", { name: "Group behavior" });
    const firstRadio = within(group).getByRole("radio", { name: "Mention only" });
    const secondRadio = within(group).getByRole("radio", { name: "All messages" });

    expect(group).toHaveAttribute("id", "channel-field-channels-discord-groupPolicy-group");
    expect(group).toHaveAttribute("aria-invalid", "true");
    expect(group).toHaveAccessibleDescription(
      "Required to complete setup.",
    );
    expect(firstRadio).toHaveAttribute("id", "channel-field-channels-discord-groupPolicy");
    expect(secondRadio).toHaveAttribute("id", "channel-field-channels-discord-groupPolicy-1");
    expect(firstRadio).toHaveAttribute("aria-invalid", "true");
    expect(firstRadio).toHaveAccessibleDescription(
      "Required to complete setup.",
    );

    document.getElementById("channel-field-channels-discord-groupPolicy")?.focus();
    expect(firstRadio).toHaveFocus();
  });

  it("associates field errors and saved-secret removal actions", () => {
    const onClearSecret = vi.fn();
    render(
      <CredentialForm
        fields={[fields[0]!]}
        values={{}}
        configuredFields={new Set(["channels.discord.token"])}
        visibleSecrets={{}}
        onChange={vi.fn()}
        onToggleSecret={vi.fn()}
        errors={{ "channels.discord.token": "Required to complete setup." }}
        onClearSecret={onClearSecret}
        showSecretActions
      />,
    );

    const token = screen.getByLabelText("Bot token");
    expect(token).toHaveAttribute("aria-invalid", "true");
    expect(token).toHaveAccessibleDescription("Required to complete setup.");
    fireEvent.click(screen.getByRole("button", { name: "Remove credentials" }));
    expect(onClearSecret).toHaveBeenCalledWith("channels.discord.token", true);
  });

  it("uses null only for an explicitly cleared secret", () => {
    expect(
      channelValuesForSubmit(
        fields,
        { "channels.matrix.password": "" },
        new Set(),
        new Set(["channels.matrix.password"]),
      ),
    ).toEqual({ "channels.matrix.password": null });
    expect(channelValuesForSubmit(fields, {}, new Set())).toEqual({});
  });
});
