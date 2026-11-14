import type { ReactNode } from "react";
import { BookOpen, ExternalLink, Github, MessageCircle } from "lucide-react";
import { useTranslation } from "react-i18next";

import { SettingsGroup, SettingsRow } from "@/components/settings/shared/SettingsControls";

export function AboutSettingsLayout({ versionInfo, links, starLink }: {
  versionInfo: ReactNode;
  links: ReactNode;
  starLink: ReactNode;
}) {
  return <div className="flex flex-1 flex-col gap-5">
    <div className="flex flex-col items-center gap-3 py-6 text-center">
      <img src="/brand/nanobot_mark.svg" alt="" className="h-16 w-16 select-none" draggable={false} />
      <h1><img src="/brand/nanobot_wordmark.svg" alt="nanobot" width={800} height={164} className="h-auto w-40 select-none dark:brightness-150" draggable={false} /></h1>
    </div>
    {versionInfo}
    {links}
    <div className="mt-auto pt-8 text-center">{starLink}</div>
  </div>;
}

export function AboutSettingsView({ reportIssueUrl, currentVersion, currentCommit, starLink }: {
  reportIssueUrl: string;
  currentVersion?: string;
  currentCommit?: string | null;
  starLink: ReactNode;
}) {
  const { t } = useTranslation();
  const links = [
    { key: "sourceCode", icon: Github, href: "https://github.com/HKUDS/nanobot" },
    { key: "documentation", icon: BookOpen, href: "https://nanobot.wiki/" },
    { key: "reportIssue", icon: MessageCircle, href: reportIssueUrl },
  ];
  return (
    <AboutSettingsLayout versionInfo={<SettingsGroup>
      <SettingsRow title={<>
        <span>{t("settings.about.version")}</span>
        <div className="mt-1 flex flex-wrap items-baseline gap-x-2 text-[13px] font-normal leading-5 tabular-nums text-muted-foreground">
          <span className="min-w-0 break-all">
            {currentVersion ? `v${currentVersion}` : "nanobot"}
            {currentCommit && <>
              <span aria-hidden> (</span>
              <a href={`https://github.com/HKUDS/nanobot/commit/${currentCommit}`}
                target="_blank" rel="noopener noreferrer" title={currentCommit}
                className="font-mono hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                {currentCommit.slice(0, 7)}
              </a>
              <span aria-hidden>)</span>
            </>}
          </span>
        </div>
      </>} />
    </SettingsGroup>} starLink={starLink} links={
      <SettingsGroup>
        {links.map(({ key, icon: Icon, href }) => (
          <a key={key} href={href} target="_blank" rel="noopener noreferrer"
            className="settings-list-row flex select-none items-center gap-3 text-[14px] settings-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
            <Icon className="h-4 w-4 text-muted-foreground" aria-hidden />
            <span className="flex-1">{t(`settings.about.${key}`)}</span>
            <ExternalLink className="h-3.5 w-3.5 text-muted-foreground" aria-hidden />
          </a>
        ))}
      </SettingsGroup>
    } />
  );
}
