import { Model } from "./model";
import { MemberModel } from "./member.model";


export class ProfileModel extends Model {
    member = new MemberModel();
    is_admin = false;
    is_super_admin = false;
    created_account = '';
    joined_at = '';
    boosting_since = '';
    hype_squad = '';
    level = 0;
    total_xp = 0;
    text_msg_xp = 0;
    voice_xp = 0;
    boost_xp = 0;
    boost_xp_multiplier = 0;
    boosting = null;
    boosting_name = null;
    boosting_remaining_days = null;
    boosting_remaining_hours = null;
    boosts = [];
    boosts_raw_data = [];
    promo_boost_xp_multiplier = 0;
    promo_boosts = [];
    promo_boosts_raw_data = [];
    promo_code_expires_hours = 0;
    can_redeem_promo_code = false;
    promo_user_set_level = 0;

    constructor(data = {}) {
        super();
        this.assign(data);
    }
}
