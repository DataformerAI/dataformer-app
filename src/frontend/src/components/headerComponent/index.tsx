import { useContext } from "react";
import { FaDiscord, FaGithub } from "react-icons/fa";
import { RiTwitterXFill } from "react-icons/ri";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import AlertDropdown from "../../alerts/alertDropDown";
import profileCircle from "../../assets/profile-circle.png";
import {
  BACKEND_URL,
  BASE_URL_API,
  LOCATIONS_TO_RETURN,
  USER_PROJECTS_HEADER,
} from "../../constants/constants";
import { AuthContext } from "../../contexts/authContext";

import useAlertStore from "../../stores/alertStore";
import { useDarkStore } from "../../stores/darkStore";
import useFlowStore from "../../stores/flowStore";
import useFlowsManagerStore from "../../stores/flowsManagerStore";
import { useLocationStore } from "../../stores/locationStore";
import { useStoreStore } from "../../stores/storeStore";
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

  const routeHistory = useLocationStore((state) => state.routeHistory);

  async function checkForChanges(): Promise<void> {
    if (nodes.length === 0) {
      await removeFlow(id!);
    }
  }

  const redirectToLastLocation = () => {
    const lastFlowVisitedIndex = routeHistory
      .reverse()
      .findIndex(
        (path) => path.includes("/flow/") && path !== location.pathname,
      );

    const lastFlowVisited = routeHistory[lastFlowVisitedIndex];
    lastFlowVisited && !location.pathname.includes("/flow")
      ? navigate(lastFlowVisited)
      : navigate("/all");
  };

  const visitedFlowPathBefore = () => {
    const last100VisitedPaths = routeHistory.slice(-99);
    return last100VisitedPaths.some((path) => path.includes("/flow/"));
  };

  const showArrowReturnIcon =
    LOCATIONS_TO_RETURN.some((path) => location.pathname.includes(path)) &&
    visitedFlowPathBefore();

  return (
    <div className="header-arrangement">
      <div className="header-start-display lg:w-[407px]">
        <Link to="/all" className="cursor-pointer" onClick={checkForChanges}>
          <span className="ml-4 text-2xl">DATAFORMER</span>
        </Link>
        {showArrowReturnIcon && (
          <Button
            variant="none"
            size="none"
            onClick={() => {
              checkForChanges();
              redirectToLastLocation();
            }}
          >
            <IconComponent name="ChevronLeft" className="w-4" />
          </Button>
        )}

        <MenuBar />
      </div>

      <div className="round-button-div">
        <Link to="/">
          <Button
            className="gap-2"
            variant={
              location.pathname === "/all" ||
              location.pathname === "/components"
                ? "primary"
                : "secondary"
            }
            size="sm"
            onClick={checkForChanges}
          >
            <IconComponent name="Home" className="h-4 w-4" />
            <div className="hidden flex-1 md:block">{USER_PROJECTS_HEADER}</div>
          </Button>
        </Link>

        {hasStore && (
          <Link to="/store">
            <Button
              className="gap-2"
              variant={location.pathname === "/store" ? "primary" : "secondary"}
              size="sm"
              onClick={checkForChanges}
              data-testid="button-store"
            >
              <IconComponent name="Store" className="h-4 w-4" />
              <div className="flex-1">Store</div>
            </Button>
          </Link>
        )}
      </div>
      <div className="header-end-division lg:w-[407px]">
        <div className="header-end-display">
          <a
            href="https://twitter.com/dataformer_ai"
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

          <>
            <Separator orientation="vertical" />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="none"
                  size="none"
                  data-testid="user-profile-settings"
                  className="shrink-0"
                >
                  <img
                    src={
                      `${BACKEND_URL.slice(
                        0,
                        BACKEND_URL.length - 1,
                      )}${BASE_URL_API}files/profile_pictures/${
                        userData?.profile_image ?? "Space/046-rocket.png"
                      }` ?? profileCircle
                    }
                    className="h-7 w-7 shrink-0 focus-visible:outline-0"
                  />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {!autoLogin && (
                  <>
                    <DropdownMenuLabel>
                      <div className="flex items-center gap-3">
                        <img
                          src={
                            `${BACKEND_URL.slice(
                              0,
                              BACKEND_URL.length - 1,
                            )}${BASE_URL_API}files/profile_pictures/${
                              userData?.profile_image
                            }` ?? profileCircle
                          }
                          className="h-5 w-5 focus-visible:outline-0 "
                        />

                        {userData?.username ?? "User"}
                      </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                  </>
                )}
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
