import React from "react";
import PropTypes from "prop-types";

import { connect } from "react-redux";
import { submit_validation } from "../../actions/submit";


class Context extends React.Component {
    static propTypes = {
        options: PropTypes.object.isRequired,
        context: PropTypes.object.isRequired,
        current: PropTypes.number.isRequired,

        submit_validation: PropTypes.func.isRequired,
    };

    constructor(props) {
        super(props);

        this.state = {
            value: null,
        }
    }

    *fields() {
        const names = Object.keys(this.props.options).filter(index => {
            return !this.props.options[index].write_only;
        });

        for (let i=0; i < names.length; i++) {
            if (this.props.options[names[i]].type === "base64/png") {
                yield <img src={`data:image/png;base64,${this.props.context[names[i]]}`}
                           alt="Can not show QR code"
                           key={i}
                />;
            }

        }
    }

    onSubmit(e) {
        if (this.state.value === null)
            return;

        this.props.submit_validation(this.props.current, this.state.value);
        this.props.history.push("/");
    }

    onChange(e) {
        this.setState({value: e.target.value})
    }

    render() {
        return (
            <div>

                {[...this.fields()]}

                <input name="value" type="text"  onChange={this.onChange.bind(this)} />
                <input name="submit" type="submit" onClick={this.onSubmit.bind(this)} />
            </div>
        );
    }
}
const mapStateToProps = state => ({
    current: state.register.current,
    context: state.register.context,
    options: state.register.options,
});


export default connect(mapStateToProps, {submit_validation})(Context);
