#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
    private_key_content='private_key content'
    private_key_path=key1
    echo -n $private_key_content > $private_key_path

    second_key_content='second_key content'
    second_key_path=key2
    echo -n $second_key_content > $second_key_path
}

teardown() {
    rm $private_key_path
    rm $second_key_path
}


@test "Identity help by arg" {
    run termius identity --help
    [ "$status" -eq 0 ]
}

@test "Identity help command" {
    run termius help identity
    [ "$status" -eq 0 ]
}

@test "Add general identity" {
    run termius identity -L local --username 'ROOT' --password 'pa'
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    identity=${lines[1]}
    [ "$(get_model_field 'identity_set' $identity 'label')" = '"local"' ]
    [ "$(get_model_field 'identity_set' $identity 'username')" = '"ROOT"' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'true' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Add identity with key" {
    run termius identity -L local --identity-file $private_key_path --debug
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    [ $(get_models_set_length 'sshkeycrypt_set') -eq 1 ]
    identity=${lines[1]}
    [ "$(get_model_field 'identity_set' $identity 'label')" = '"local"' ]
    [ "$(get_model_field 'identity_set' $identity 'username')" = 'null' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'true' ]
    ssh_key=$(get_model_field 'identity_set' $identity 'ssh_key')
    [ $(get_model_field 'sshkeycrypt_set' $ssh_key 'label') = '"key1"' ]
    [ "$(get_model_field 'sshkeycrypt_set' $ssh_key 'private_key')" = "\"$private_key_content\"" ]
}

@test "Update identity" {
    identity=$(termius identity -L local --username 'ROOT' --password 'pa')
    run termius identity --password 'ps' $identity
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
    [ "$(get_model_field 'identity_set' $identity 'label')" = '"local"' ]
    [ "$(get_model_field 'identity_set' $identity 'username')" = '"ROOT"' ]
    [ "$(get_model_field 'identity_set' $identity 'password')" = '"ps"' ]
    [ $(get_model_field 'identity_set' $identity 'is_visible') = 'true' ]
    [ $(get_model_field 'identity_set' $identity 'ssh_key') = 'null' ]
}

@test "Update many identities" {
    identity1=$(termius identity -L local --username 'ROOT' --password 'pa')
    identity2=$(termius identity -L local --username 'ROOT' --password 'pa')
    run termius identity -L local --username 'ROOT' --password 'pa' $identity1 $identity2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'identity_set') -eq 2 ]
}

@test "Delete identity" {
    identity1=$(termius identity -L local --username 'ROOT' --password 'pa')
    identity2=$(termius identity -L local --username 'ROOT' --password 'pa')
    run termius identity --delete $identity2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
}

@test "Delete many identities" {
    identity1=$(termius identity -L local --username 'ROOT' --password 'pa')
    identity2=$(termius identity -L local --username 'ROOT' --password 'pa')
    run termius identity --delete $identity1 $identity2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'identity_set') -eq 0 ]
}
