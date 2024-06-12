import ForwardedIconComponent from "../../../../../components/genericIconComponent";
import RenderIcons from "../../../../../components/renderIconComponent";
import { toolbarSelectItemProps } from "../../../../../types/components";

export default function ToolbarSelectItem({
  value,
  icon,
  style,
  dataTestId,
  ping,
  shortcut,
}: toolbarSelectItemProps) {
  const isMac = navigator.platform.toUpperCase().includes("MAC");
  let hasShift = false;
  const fixedShortcut = shortcut?.split("+");
  fixedShortcut.forEach((key) => {
    if (key.toLowerCase().includes("shift")) {
      hasShift = true;
    }
  });
  const filteredShortcut = fixedShortcut.filter(
    (key) => !key.toLowerCase().includes("shift"),
  );
  let shortcutWPlus: string[] = [];
  if (!hasShift) shortcutWPlus = filteredShortcut.join("+").split(" ");

  return (
    <div className={`flex ${style}`} data-testid={dataTestId}>
      <ForwardedIconComponent
        name={icon}
        className={`   mr-2  ${
          icon === "Share3"
            ? "absolute left-2  top-[0.25em] h-6 w-6"
            : "mt-[0.15em] h-4 w-4"
        }   ${ping && "animate-pulse text-green-500"}`}
      />
      <span className={`${icon === "Share3" ? "ml-[1.8em]" : " "}`}>
        {value}
      </span>
      <span
        className={`absolute right-2 top-[0.43em] flex items-center rounded-sm bg-muted px-1.5 py-[0.1em] text-muted-foreground `}
      >
        <RenderIcons
          isMac={isMac}
          hasShift={hasShift}
          filteredShortcut={filteredShortcut}
          shortcutWPlus={shortcutWPlus}
        />
      </span>
    </div>
  );
}
