export const numToAccountingFormat = (amount: number) => {
    if (amount === 0) {
        return '-';
    }
    let amount_string = (amount / 100).toLocaleString();
    if (!amount_string.split('.')[1]) {
        amount_string = `${amount_string}.00`;
    }
    if (amount_string.split('.')[1].length === 1) {
        amount_string = `${amount_string}0`;
    }
    if (amount < 0) {
        return `($${amount_string.slice(1)})`;
    }
    return `$${amount_string}`;
};

export const snakeCaseToSentence = (str: string) => {
    const words = str.split('_');
    const capitalized = words.map(
        (word) => word[0].toUpperCase() + word.slice(1)
    );
    return capitalized.join(' ');
};
