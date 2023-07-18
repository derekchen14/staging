import { writable } from 'svelte/store';

// Store the users as an array of objects
export const users = [
  { username: 'best@soleda.ai', password: '123456' },
  // Add more user objects here as needed
];

// Export the writable store
export const store = writable(null);

export const getUserDetails = async (username, password) => {
  // Check if the given username and password match any user object in the array
  const matchedUser = users.find((user) => user.username === username && user.password === password);

  // If a user is found, return a value indicating success (you can modify this as needed)
  if (matchedUser) {
    return 1;
  }

  // If the user is not found, return a value indicating failure (you can modify this as needed)
  return 0;
};
