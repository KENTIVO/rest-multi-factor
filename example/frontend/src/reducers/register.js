import {

    SET_REGISTER_CURRENT,
    SET_REGISTER_DEVICES,
    SET_REGISTER_OPTIONS,
    SET_REGISTER_CONTEXT,
    CLR_REGISTER_REDUCER,

} from "./types";


const initialState = {
    devices: [],
    options: {},
    context: null,
    current: null,
};


export default function(state=initialState, actions) {
    if (actions.type === SET_REGISTER_DEVICES)
        return {...state, devices: actions.data};

    if (actions.type === SET_REGISTER_CURRENT)
        return {...state, current: actions.data};

    if (actions.type === SET_REGISTER_CONTEXT)
        return {...state, context: actions.data};

    if (actions.type === SET_REGISTER_OPTIONS)
        return {...state, options: actions.data.actions["POST"]};

    if (actions.type === CLR_REGISTER_REDUCER)
        return initialState;

    return state;
}
