export const host = "http://localhost:5000";

export const loginRoute = `${host}/api/auth/login`;
export const registerRoute = `${host}/api/auth/register`;
export const logoutRoute = `${host}/api/auth/logout`;
export const allUsersRoute = `${host}/api/auth/allusers`;
export const sendMessageRoute = `${host}/api/messages/addmsg`;
export const recieveMessageRoute = `${host}/api/messages/getmsg`;
export const setAvatarRoute = `${host}/api/auth/setavatar`;

// File sharing routes
export const uploadFileRoute = `${host}/api/files/upload`;
export const downloadFileRoute = `${host}/api/files/download`;
export const previewFileRoute = `${host}/api/files/preview`;
export const fileInfoRoute = `${host}/api/files/info`;

// Self-destruct timer routes
export const setSelfDestructRoute = `${host}/api/self-destruct/set-timer`;
export const getSelfDestructRoute = `${host}/api/self-destruct/get-timer`;
export const getConversationTimerRoute = `${host}/api/self-destruct/conversation-info`;
export const cancelConversationTimerRoute = `${host}/api/self-destruct/cancel-conversation-timer`;
export const activateTimerRoute = `${host}/api/self-destruct/activate-timer`;
