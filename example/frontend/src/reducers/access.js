import {

    ACCESS_GRANTED,

} from "./types";


const initialState = {
    content: "Access denied",
};

export default function (state = initialState, action) {
    if (action.type === ACCESS_GRANTED)
        return {content: action.data};

    return state;
}
