import * as React from 'react';

const PrimaryButton = ({
    children,
    onClick = () => {},
    disabled,
    type = 'button',
}: {
    children: React.ReactNode;
    onClick?: () => void;
    disabled?: boolean;
    type?: 'button' | 'submit';
}) => {
    return (
        <button
            disabled={disabled}
            className="bg-green-500 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-full shadow-lg text-sm"
            onClick={onClick}
            type={type}
        >
            {children}
        </button>
    );
};

export default PrimaryButton;
