function formatCount(value) {
  const number = Number(value) || 0;
  if (number < 1000) {
    return `${number}`;
  }
  if (number < 10000) {
    const compact = Math.floor(number / 100) / 10;
    return `${compact}k`;
  }
  return `${Math.floor(number / 1000)}k`;
}

export default {
  formatCount,
};
