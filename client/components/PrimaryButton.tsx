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
            className={`
                ${
                    disabled
                        ? 'bg-green-100 cursor-not-allowed text-gray-500'
                        : 'bg-green-500 hover:bg-green-700 shadow-lg text-white'
                }
                font-semibold py-2 px-4 rounded-full text-sm
            `}
            onClick={onClick}
            type={type}
        >
            {children}
        </button>
    );
};

export default PrimaryButton;
