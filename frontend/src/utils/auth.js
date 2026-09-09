/**
 * Decode the `exp` claim from a JWT without a library.
 * Returns true if the token is valid (not expired).
 */
export function isTokenValid(token) {
  if (!token) return false;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    // exp is Unix timestamp in seconds
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}
