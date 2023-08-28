import * as React from "react";
import { Cog6ToothIcon } from "@heroicons/react/24/solid";
import { Menu } from "@headlessui/react";

const ConnectionMenu = ({ disconnect }: { disconnect: () => void }) => (
  <Menu>
    <Menu.Button>
      <Cog6ToothIcon className="absolute top-0 right-0 h-5 w-5 cursor-pointer text-gray-400 hover:text-gray-700" />
    </Menu.Button>
    <Menu.Items className="absolute right-0 bg-white shadow-lg p-2">
      <Menu.Item>
        <button
          className="mt-2 inline-block hover:bg-slate-200 text-red-500 font-bold py-2 px-4 rounded-full text-sm"
          onClick={disconnect}
        >
          Disconnect
        </button>
      </Menu.Item>
    </Menu.Items>
  </Menu>
);

const ConnectionCard = ({
  title,
  isConnected,
  children,
  disconnect,
}: {
  title: string;
  isConnected: boolean;
  children: React.ReactNode;
  disconnect: () => void;
}) => (
  <div className="shadow-lg p-4 mb-2 relative">
    {isConnected && <ConnectionMenu disconnect={disconnect} />}
    <h3 className="font-semibold mb-2">{title}</h3>
    {children}
  </div>
);

export default ConnectionCard;
