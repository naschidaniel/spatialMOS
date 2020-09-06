export function DataExchangeObject(attributes) {
  if (attributes === undefined) return {}
  else {
    let data = attributes.value.split("'").join('"');
    return JSON.parse(data);
  }
}

export function DataExchangeString(attributes) {
  return attributes?.value;
}
