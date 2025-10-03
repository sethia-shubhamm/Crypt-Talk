// Automatically detect environment and set appropriate host
export const host = process.env.NODE_ENV === 'production' 
  ? window.location.origin  // Use same domain in production
  : "http://localhost:5000"; // Use localhost in development

export const loginRoute = `${host}/api/auth/login`;
export const registerRoute = `${host}/api/auth/register`;
export const logoutRoute = `${host}/api/auth/logout`;
export const allUsersRoute = `${host}/api/auth/allusers`;
export const sendMessageRoute = `${host}/api/messages/addmsg`;
export const recieveMessageRoute = `${host}/api/messages/getmsg`;
export const setAvatarRoute = `${host}/api/auth/setavatar`;
