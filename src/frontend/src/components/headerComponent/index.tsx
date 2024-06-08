import { useContext } from "react";
import { FaDiscord, FaGithub } from "react-icons/fa";
import { RiTwitterXFill } from "react-icons/ri";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import AlertDropdown from "../../alerts/alertDropDown";
import { USER_PROJECTS_HEADER } from "../../constants/constants";
import { AuthContext } from "../../contexts/authContext";

import { Node } from "reactflow";
import useAlertStore from "../../stores/alertStore";
import { useDarkStore } from "../../stores/darkStore";
import useFlowStore from "../../stores/flowStore";
import useFlowsManagerStore from "../../stores/flowsManagerStore";
import { useStoreStore } from "../../stores/storeStore";
import { gradients } from "../../utils/styleUtils";
import IconComponent from "../genericIconComponent";
import { Button } from "../ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Separator } from "../ui/separator";
import MenuBar from "./components/menuBar";

export default function Header(): JSX.Element {
  const notificationCenter = useAlertStore((state) => state.notificationCenter);
  const location = useLocation();
  const { logout, autoLogin, isAdmin, userData } = useContext(AuthContext);
  const navigate = useNavigate();
  const removeFlow = useFlowsManagerStore((store) => store.removeFlow);
  const hasStore = useStoreStore((state) => state.hasStore);
  const { id } = useParams();
  const nodes = useFlowStore((state) => state.nodes);

  const dark = useDarkStore((state) => state.dark);
  const setDark = useDarkStore((state) => state.setDark);
  const stars = useDarkStore((state) => state.stars);

  async function checkForChanges(nodes: Node[]): Promise<void> {
    if (nodes.length === 0) {
      await removeFlow(id!);
    }
  }

  return (
    <div className="header-arrangement">
      <div className="header-start-display lg:w-[30%]">
        <Link to="/" onClick={() => checkForChanges(nodes)}>
          <span className="ml-4 text-2xl">DATAFORMER</span>
        </Link>
        <MenuBar removeFunction={checkForChanges} />
      </div>
      <div className="round-button-div">
        <Link to="/">
          <Button
            className="gap-2"
            variant={
              location.pathname === "/flows" ||
              location.pathname === "/components"
                ? "primary"
                : "secondary"
            }
            size="sm"
            onClick={() => {
              checkForChanges(nodes);
            }}
          >
            <IconComponent name="Home" className="h-4 w-4" />
            <div className="hidden flex-1 md:block">{USER_PROJECTS_HEADER}</div>
          </Button>
        </Link>
        {/* <Link to="/community">
          <Button
            className="gap-2"
            variant={
              location.pathname === "/community" ? "primary" : "secondary"
            }
            size="sm"
          >
            <IconComponent name="Users2" className="h-4 w-4" />
            <div className="flex-1">Community Examples</div>
          </Button>
        </Link> */}
        {hasStore && (
          <Link to="/store">
            <Button
              className="gap-2"
              variant={location.pathname === "/store" ? "primary" : "secondary"}
              size="sm"
              onClick={() => {
                checkForChanges(nodes);
              }}
              data-testid="button-store"
            >
              <IconComponent name="Store" className="h-4 w-4" />
              <div className="flex-1">Store</div>
            </Button>
          </Link>
        )}
      </div>
      <div className="header-end-division lg:w-[30%]">
        <div className="header-end-display">
          <a
            href="https://x.com/SatpalPatawat"
            target="_blank"
            rel="noreferrer"
            className="text-muted-foreground"
          >
            <RiTwitterXFill className="side-bar-button-size" />
          </a>
          <a
            href="https://dataformer.ai/discord"
            target="_blank"
            rel="noreferrer"
            className="text-muted-foreground"
          >
            <FaDiscord className="side-bar-button-size" />
          </a>

          <Separator orientation="vertical" />
          <button
            className="extra-side-bar-save-disable"
            onClick={() => {
              setDark(!dark);
            }}
          >
            {dark ? (
              <IconComponent name="SunIcon" className="side-bar-button-size" />
            ) : (
              <IconComponent name="MoonIcon" className="side-bar-button-size" />
            )}
          </button>
          <AlertDropdown>
            <div className="extra-side-bar-save-disable relative">
              {notificationCenter && (
                <div className="header-notifications"></div>
              )}
              <IconComponent
                name="Bell"
                className="side-bar-button-size"
                aria-hidden="true"
              />
            </div>
          </AlertDropdown>
          {!autoLogin && (
            <button
              onClick={() => {
                navigate("/account/api-keys");
              }}
            >
              <IconComponent
                name="Key"
                className="side-bar-button-size text-muted-foreground hover:text-accent-foreground"
              />
            </button>
          )}

          <>
            <Separator orientation="vertical" />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  data-testid="user-profile-settings"
                  className={
                    "h-7 w-7 rounded-full focus-visible:outline-0 " +
                    (userData?.profile_image ??
                      (userData?.id
                        ? gradients[
                            parseInt(userData?.id ?? "", 30) % gradients.length
                          ]
                        : "bg-gray-500"))
                  }
                />
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuLabel>General</DropdownMenuLabel>
                <DropdownMenuItem
                  className="cursor-pointer"
                  onClick={() => navigate("/settings")}
                >
                  Settings
                </DropdownMenuItem>
                {!autoLogin && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuLabel>My Account</DropdownMenuLabel>
                    {isAdmin && (
                      <DropdownMenuItem
                        className="cursor-pointer"
                        onClick={() => navigate("/admin")}
                      >
                        Admin Page
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuItem
                      className="cursor-pointer"
                      onClick={() => {
                        logout();
                      }}
                    >
                      Sign Out
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </>
        </div>
      </div>
    </div>
  );
}
