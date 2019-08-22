import {

    SET_VALIDATE_DEVICES,

} from "./types";

const initialState = {
    devices: [],
};

export default function(state=initialState, action) {
    if (action.type === SET_VALIDATE_DEVICES)
        return {...state, devices: action.data};

    return state;
}
